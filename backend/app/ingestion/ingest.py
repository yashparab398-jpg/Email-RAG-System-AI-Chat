import csv
import sys
import time
import hashlib

import pandas as pd
from pathlib import Path

from pymongo.errors import (
    BulkWriteError,
    PyMongoError,
    NetworkTimeout,
    AutoReconnect,
    ConnectionFailure,
    ServerSelectionTimeoutError,
    ExecutionTimeout,
)

from app.database.mongodb import (
    emails_collection,
    failed_collection,
)

from app.parsing.email_parser import parse_email
from app.parsing.email_cleaner import clean_email


# =========================================================
# CONFIGURATION
# =========================================================

DATASET_PATH = Path(
    "../dataset/emails.csv"
)

# Number of CSV rows read at a time.
#
# Keep this at 1000 because parsing is independent
# from MongoDB write size.
BATCH_SIZE = 1000


# MongoDB write size.
#
# Smaller database batches reduce the chance of a
# 30-second MongoDB network timeout.
DB_WRITE_BATCH_SIZE = 250


# Number of times to retry a temporary MongoDB failure.
MONGO_MAX_RETRIES = 4


# Initial delay between MongoDB retries.
MONGO_RETRY_DELAY = 2


# =========================================================
# CSV FIELD LIMIT
# =========================================================

def configure_csv_field_limit():

    """
    Increase Python's CSV field-size limit.

    Enron emails can contain very large message fields
    that exceed Python's default 131072-byte limit.
    """

    limit = sys.maxsize

    while True:

        try:

            csv.field_size_limit(
                limit
            )

            break

        except OverflowError:

            limit //= 10


# Configure once when this module is loaded.
configure_csv_field_limit()


# =========================================================
# EMAIL ID
# =========================================================

def create_email_id(
    file_path,
    message
):
    """
    Create a deterministic ID for an email.

    The same dataset row will therefore receive the
    same MongoDB _id if it is processed again.

    This protects against duplicate insertion when a
    MongoDB write times out after the server has already
    inserted some records.
    """

    source = (
        str(file_path or "")
        + "\0"
        + str(message or "")
    )

    return hashlib.sha256(
        source.encode(
            "utf-8",
            errors="replace"
        )
    ).hexdigest()


# =========================================================
# TEMPORARY MONGODB ERROR
# =========================================================

def is_retryable_mongo_error(
    error
):
    """
    Determine whether a MongoDB error is likely temporary.

    These errors commonly occur when MongoDB is busy,
    restarting, temporarily unreachable, or a socket
    operation exceeds its timeout.
    """

    return isinstance(
        error,
        (
            NetworkTimeout,
            AutoReconnect,
            ConnectionFailure,
            ServerSelectionTimeoutError,
            ExecutionTimeout,
        )
    )


# =========================================================
# MONGODB INSERT
# =========================================================

def insert_email_documents(
    documents
):
    """
    Insert email documents into MongoDB safely.

    Features:
    - smaller write batches
    - retries for temporary MongoDB failures
    - deterministic _id values
    - duplicate-safe retries
    """

    if not documents:
        return 0

    total_inserted = 0

    # -----------------------------------------------------
    # SPLIT INTO SMALLER DATABASE WRITE BATCHES
    # -----------------------------------------------------

    for start in range(
        0,
        len(documents),
        DB_WRITE_BATCH_SIZE
    ):

        write_batch = documents[
            start:
            start + DB_WRITE_BATCH_SIZE
        ]

        attempt = 0

        while True:

            try:

                result = (
                    emails_collection.insert_many(
                        write_batch,
                        ordered=False,
                    )
                )

                total_inserted += len(
                    result.inserted_ids
                )

                break

            except BulkWriteError as error:

                details = (
                    error.details or {}
                )

                inserted = int(
                    details.get(
                        "nInserted",
                        0
                    )
                    or 0
                )

                total_inserted += inserted

                write_errors = (
                    details.get(
                        "writeErrors",
                        []
                    )
                )

                duplicate_errors = 0
                other_errors = 0

                for write_error in write_errors:

                    code = write_error.get(
                        "code"
                    )

                    if code == 11000:
                        duplicate_errors += 1
                    else:
                        other_errors += 1

                print(
                    "[INGESTION] MongoDB bulk write: "
                    f"inserted={inserted}, "
                    f"duplicates={duplicate_errors}, "
                    f"other_errors={other_errors}",
                    flush=True
                )

                # -------------------------------------------------
                # Duplicate records are safe.
                #
                # They mean the deterministic _id already exists,
                # which can happen when a previous MongoDB attempt
                # succeeded before the client received its response.
                # -------------------------------------------------

                if other_errors == 0:

                    break

                # -------------------------------------------------
                # Non-duplicate bulk errors should not be silently
                # converted into failed emails.
                # -------------------------------------------------

                raise


            except PyMongoError as error:

                print(
                    "[INGESTION] MongoDB write failed:",
                    repr(error),
                    flush=True
                )

                # -------------------------------------------------
                # RETRY TEMPORARY DATABASE FAILURES
                # -------------------------------------------------

                if not is_retryable_mongo_error(
                    error
                ):

                    raise

                attempt += 1

                if attempt > MONGO_MAX_RETRIES:

                    print(
                        "[INGESTION] MongoDB write "
                        "retry limit reached.",
                        flush=True
                    )

                    # IMPORTANT:
                    #
                    # Raise instead of pretending these emails
                    # failed. ingestion.py will leave the dataset
                    # checkpoint unchanged for this batch.
                    raise

                delay = (
                    MONGO_RETRY_DELAY
                    * attempt
                )

                print(
                    "[INGESTION] Retrying MongoDB "
                    f"write in {delay}s "
                    f"(attempt {attempt}/"
                    f"{MONGO_MAX_RETRIES})...",
                    flush=True
                )

                time.sleep(
                    delay
                )

    return total_inserted


# =========================================================
# FAILED RECORD INSERT
# =========================================================

def insert_failed_documents(
    documents
):
    """
    Store genuine parsing failures.

    MongoDB availability problems are NOT passed here.
    """

    if not documents:
        return

    for start in range(
        0,
        len(documents),
        DB_WRITE_BATCH_SIZE
    ):

        write_batch = documents[
            start:
            start + DB_WRITE_BATCH_SIZE
        ]

        attempt = 0

        while True:

            try:

                failed_collection.insert_many(
                    write_batch,
                    ordered=False,
                )

                break

            except BulkWriteError as error:

                print(
                    "[INGESTION] Failed-record "
                    "bulk write warning:",
                    repr(error),
                    flush=True
                )

                # Failed records do not need to stop
                # ingestion because the original email
                # processing failure has already been recorded.
                break

            except PyMongoError as error:

                print(
                    "[INGESTION] Failed-record "
                    "MongoDB write failed:",
                    repr(error),
                    flush=True
                )

                if not is_retryable_mongo_error(
                    error
                ):

                    break

                attempt += 1

                if attempt > MONGO_MAX_RETRIES:

                    print(
                        "[INGESTION] Failed-record "
                        "MongoDB retry limit reached. "
                        "Continuing ingestion.",
                        flush=True
                    )

                    break

                delay = (
                    MONGO_RETRY_DELAY
                    * attempt
                )

                time.sleep(
                    delay
                )


# =========================================================
# READ DATASET
# =========================================================

def read_email_batches(
    start_row=0
):
    """
    Stream the Enron CSV in manageable batches.

    start_row represents the number of dataset
    data rows that have already been consumed.

    This allows ingestion to resume after an
    interruption without using pandas skiprows.

    The CSV is streamed using Python's csv module
    so very large email message fields can be handled.
    """

    start_row = max(
        0,
        int(start_row or 0)
    )

    print(
        f"[INGESTION] Opening dataset: "
        f"{DATASET_PATH}",
        flush=True
    )

    # -----------------------------------------------------
    # OPEN CSV
    # -----------------------------------------------------

    with open(
        DATASET_PATH,
        "r",
        encoding="utf-8",
        errors="replace",
        newline=""
    ) as file:

        reader = csv.DictReader(
            file
        )

        # -------------------------------------------------
        # VALIDATE HEADER
        # -------------------------------------------------

        if reader.fieldnames is None:

            raise RuntimeError(
                "Dataset CSV has no header."
            )

        print(
            "[INGESTION] Dataset columns:",
            reader.fieldnames,
            flush=True
        )

        # -------------------------------------------------
        # RESUME
        # -------------------------------------------------

        if start_row > 0:

            print(
                f"[INGESTION] Skipping "
                f"{start_row:,} previously processed "
                f"dataset rows...",
                flush=True
            )

            skipped = 0

            while skipped < start_row:

                try:

                    next(reader)

                except StopIteration:

                    print(
                        "[INGESTION] Dataset ended while "
                        "resuming.",
                        flush=True
                    )

                    return

                skipped += 1

                # -------------------------------------------------
                # PERIODIC RESUME PROGRESS
                # -------------------------------------------------

                if skipped % 10000 == 0:

                    print(
                        f"[INGESTION] Resume position: "
                        f"{skipped:,}/{start_row:,}",
                        flush=True
                    )

        print(
            f"[INGESTION] Starting dataset processing "
            f"from row {start_row:,}.",
            flush=True
        )

        # -----------------------------------------------------
        # BUILD BATCHES
        # -----------------------------------------------------

        batch = []

        for row in reader:

            batch.append(
                row
            )

            # -------------------------------------------------
            # FULL BATCH
            # -------------------------------------------------

            if len(batch) >= BATCH_SIZE:

                yield pd.DataFrame(
                    batch
                )

                batch = []

        # -----------------------------------------------------
        # FINAL PARTIAL BATCH
        # -----------------------------------------------------

        if batch:

            yield pd.DataFrame(
                batch
            )


# =========================================================
# PROCESS ONE BATCH
# =========================================================

def process_batch(
    batch
):
    """
    Parse, clean and persist one dataset batch.

    IMPORTANT:
    A MongoDB failure raises an exception instead of
    converting the affected emails into failed records.

    This allows ingestion.py to keep the dataset checkpoint
    at the previous successful position.
    """

    parsed_emails = []
    failed_emails = []

    # -----------------------------------------------------
    # TRACK ROWS
    # -----------------------------------------------------

    rows_processed = len(
        batch
    )

    # -----------------------------------------------------
    # PARSE + CLEAN
    # -----------------------------------------------------

    for _, row in batch.iterrows():

        try:

            message = row.get(
                "message",
                ""
            )

            file_path = row.get(
                "file",
                ""
            )

            parsed = parse_email(
                message,
                file_path,
            )

            # -------------------------------------------------
            # FAILED EMAIL
            # -------------------------------------------------

            if parsed.get(
                "status"
            ) == "failed":

                failed_emails.append(
                    parsed
                )

                continue

            # -------------------------------------------------
            # CLEAN EMAIL
            # -------------------------------------------------

            parsed["status"] = (
                "processing"
            )

            parsed["clean_body"] = (
                clean_email(
                    parsed.get(
                        "body",
                        ""
                    )
                )
            )

            parsed["status"] = (
                "parsed"
            )

            # -------------------------------------------------
            # DETERMINISTIC ID
            # -------------------------------------------------
            #
            # This makes retries safe.
            # The same source email gets the same _id.
            # -------------------------------------------------

            if not parsed.get(
                "_id"
            ):

                parsed["_id"] = (
                    create_email_id(
                        file_path,
                        message
                    )
                )

            parsed_emails.append(
                parsed
            )

        except Exception as error:

            failed_emails.append(
                {
                    "error":
                        str(error),

                    "raw_body":
                        row.get(
                            "message"
                        ),

                    "folder_path":
                        row.get(
                            "file"
                        ),

                    "status":
                        "failed",
                }
            )

    # =====================================================
    # INSERT SUCCESSFUL EMAILS
    # =====================================================

    successful_count = 0

    if parsed_emails:

        # -------------------------------------------------
        # IMPORTANT
        #
        # If MongoDB fails after retries, this function
        # raises the error.
        #
        # ingestion.py will then NOT advance the dataset
        # checkpoint for this batch.
        # -------------------------------------------------

        successful_count = (
            insert_email_documents(
                parsed_emails
            )
        )

    # =====================================================
    # INSERT GENUINE FAILED RECORDS
    # =====================================================

    if failed_emails:

        insert_failed_documents(
            failed_emails
        )

    # =====================================================
    # RETURN BATCH RESULT
    # =====================================================

    return {
        "parsed":
            successful_count,

        "failed":
            len(
                failed_emails
            ),

        "rows_processed":
            rows_processed
    }