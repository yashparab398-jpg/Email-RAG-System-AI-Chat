from threading import Lock, Thread

from fastapi import APIRouter

from app.database.mongodb import (
    ingestion_collection,
)

from app.ingestion.ingest import (
    read_email_batches,
    process_batch,
)

from app.utils.logger import logger


router = APIRouter(
    prefix="/ingestion",
    tags=["Ingestion"]
)


# =========================================================
# INGESTION CONTROL
# =========================================================

_ingestion_lock = Lock()
_ingestion_thread = None


# =========================================================
# RUN INGESTION
# =========================================================

def run_ingestion():

    global _ingestion_thread

    try:

        logger.info(
            "Email ingestion started."
        )

        # -------------------------------------------------
        # READ EXISTING INGESTION STATE
        # -------------------------------------------------

        existing_status = (
            ingestion_collection.find_one(
                {}
            )
            or {}
        )

        total_processed = int(
            existing_status.get(
                "processed",
                0
            )
            or 0
        )

        total_failed = int(
            existing_status.get(
                "failed",
                0
            )
            or 0
        )

        # -------------------------------------------------
        # DATASET ROW POSITION
        # -------------------------------------------------
        #
        # IMPORTANT:
        #
        # dataset_rows_processed represents rows that have
        # actually been successfully handled.
        #
        # We NEVER use processed + failed here when the
        # checkpoint already exists.
        #
        # This prevents a MongoDB failure from accidentally
        # skipping records.
        # -------------------------------------------------

        if (
            "dataset_rows_processed"
            in existing_status
        ):

            dataset_rows_processed = int(
                existing_status.get(
                    "dataset_rows_processed",
                    0
                )
                or 0
            )

        else:

            # -------------------------------------------------
            # Legacy installation.
            #
            # Existing installation previously used:
            #
            # processed + failed
            #
            # as its dataset position.
            #
            # Preserve that behavior only for the first
            # migration into the new checkpoint system.
            # -------------------------------------------------

            dataset_rows_processed = (
                total_processed
                + total_failed
            )

        # -------------------------------------------------
        # MARK PROCESSING
        # -------------------------------------------------

        ingestion_collection.update_one(
            {},
            {
                "$set": {
                    "status":
                        "processing",

                    "processed":
                        total_processed,

                    "failed":
                        total_failed,

                    "dataset_rows_processed":
                        dataset_rows_processed
                }
            },
            upsert=True
        )

        logger.info(
            f"Resuming ingestion from dataset row "
            f"{dataset_rows_processed:,}. "
            f"Already processed: {total_processed:,} | "
            f"Failed: {total_failed:,}"
        )

        # -------------------------------------------------
        # PROCESS REMAINING EMAIL BATCHES
        # -------------------------------------------------

        for batch in read_email_batches(
            start_row=
                dataset_rows_processed
        ):

            # -------------------------------------------------
            # PROCESS BATCH
            # -------------------------------------------------
            #
            # process_batch() now raises an exception if
            # MongoDB cannot successfully persist the batch
            # after retries.
            #
            # Therefore the checkpoint below is NOT changed
            # when MongoDB fails.
            # -------------------------------------------------

            result = process_batch(
                batch
            )

            batch_processed = int(
                result.get(
                    "parsed",
                    0
                )
                or 0
            )

            batch_failed = int(
                result.get(
                    "failed",
                    0
                )
                or 0
            )

            batch_rows = int(
                result.get(
                    "rows_processed",
                    len(batch)
                )
                or 0
            )

            # -------------------------------------------------
            # UPDATE TOTALS
            # -------------------------------------------------

            total_processed += (
                batch_processed
            )

            total_failed += (
                batch_failed
            )

            # -------------------------------------------------
            # ADVANCE DATASET CHECKPOINT
            # -------------------------------------------------
            #
            # This happens ONLY after process_batch()
            # successfully returns.
            #
            # Therefore a MongoDB timeout cannot cause the
            # dataset to skip the affected batch.
            # -------------------------------------------------

            dataset_rows_processed += (
                batch_rows
            )

            logger.info(
                f"Processed: "
                f"{total_processed:,} | "
                f"Failed: "
                f"{total_failed:,} | "
                f"Dataset rows: "
                f"{dataset_rows_processed:,}"
            )

            # -------------------------------------------------
            # SAVE SUCCESSFUL CHECKPOINT
            # -------------------------------------------------

            ingestion_collection.update_one(
                {},
                {
                    "$set": {
                        "status":
                            "processing",

                        "processed":
                            total_processed,

                        "failed":
                            total_failed,

                        "dataset_rows_processed":
                            dataset_rows_processed
                    }
                },
                upsert=True
            )

        # -------------------------------------------------
        # COMPLETED
        # -------------------------------------------------

        ingestion_collection.update_one(
            {},
            {
                "$set": {
                    "status":
                        "completed",

                    "processed":
                        total_processed,

                    "failed":
                        total_failed,

                    "dataset_rows_processed":
                        dataset_rows_processed
                }
            },
            upsert=True
        )

        logger.info(
            "Email ingestion completed."
        )

    except Exception as error:

        logger.exception(
            "Email ingestion stopped because "
            "the current batch could not be completed."
        )

        # -------------------------------------------------
        # SAVE FAILURE STATE
        # -------------------------------------------------
        #
        # VERY IMPORTANT:
        #
        # We do NOT modify:
        #
        # processed
        # failed
        # dataset_rows_processed
        #
        # here.
        #
        # The last successful checkpoint remains intact.
        #
        # When ingestion is started again, it will resume
        # from that exact checkpoint.
        # -------------------------------------------------

        try:

            ingestion_collection.update_one(
                {},
                {
                    "$set": {
                        "status":
                            "failed",

                        "last_error":
                            str(error)
                    }
                },
                upsert=True
            )

        except Exception as status_error:

            logger.error(
                f"Unable to update ingestion failure "
                f"status: {status_error}"
            )

    finally:

        with _ingestion_lock:

            _ingestion_thread = None


# =========================================================
# START INGESTION
# =========================================================

@router.post("/start")
def start_ingestion():

    global _ingestion_thread

    # -----------------------------------------------------
    # PREVENT DUPLICATE INGESTION
    # -----------------------------------------------------

    with _ingestion_lock:

        if (
            _ingestion_thread is not None
            and _ingestion_thread.is_alive()
        ):

            return {
                "message":
                    "Ingestion is already running.",

                "status":
                    "processing"
            }

        # -------------------------------------------------
        # START BACKGROUND THREAD
        # -------------------------------------------------

        _ingestion_thread = Thread(
            target=run_ingestion,
            daemon=True,
            name="email-ingestion"
        )

        _ingestion_thread.start()

    return {
        "message":
            "Ingestion started or resumed.",

        "status":
            "processing"
    }


# =========================================================
# INGESTION STATUS
# =========================================================

@router.get("/status")
def get_status():

    try:

        # -------------------------------------------------
        # READ STATUS DOCUMENT
        # -------------------------------------------------

        status = (
            ingestion_collection.find_one(
                {},
                {
                    "_id": 0
                }
            )
            or {}
        )

        # -------------------------------------------------
        # NO STATUS DOCUMENT
        # -------------------------------------------------

        if not status:

            return {
                "processed": 0,

                "failed": 0,

                "ingestion": {
                    "status":
                        "ready",

                    "processed":
                        0,

                    "failed":
                        0,

                    "dataset_rows_processed":
                        0
                },

                "worker_running":
                    False,

                "dataset_rows_processed":
                    0
            }

        # -------------------------------------------------
        # NORMALIZE VALUES
        # -------------------------------------------------

        processed = int(
            status.get(
                "processed",
                0
            )
            or 0
        )

        failed = int(
            status.get(
                "failed",
                0
            )
            or 0
        )

        ingestion_status = str(
            status.get(
                "status",
                "ready"
            )
        ).lower()

        # -------------------------------------------------
        # CHECK ACTUAL PYTHON WORKER
        # -------------------------------------------------

        with _ingestion_lock:

            worker_running = (
                _ingestion_thread is not None
                and _ingestion_thread.is_alive()
            )

        # -------------------------------------------------
        # RECOVER STALE PROCESSING STATE
        # -------------------------------------------------

        if (
            ingestion_status ==
            "processing"
            and not worker_running
        ):

            ingestion_status = "ready"

        # -------------------------------------------------
        # DATASET ROW POSITION
        # -------------------------------------------------

        if (
            "dataset_rows_processed"
            in status
        ):

            dataset_rows_processed = int(
                status.get(
                    "dataset_rows_processed",
                    0
                )
                or 0
            )

        else:

            dataset_rows_processed = (
                processed
                + failed
            )

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------

        response = {
            "processed":
                processed,

            "failed":
                failed,

            "worker_running":
                worker_running,

            "dataset_rows_processed":
                dataset_rows_processed,

            "ingestion": {
                "status":
                    ingestion_status,

                "processed":
                    processed,

                "failed":
                    failed,

                "dataset_rows_processed":
                    dataset_rows_processed
            }
        }

        # -------------------------------------------------
        # INCLUDE LAST ERROR IF PRESENT
        # -------------------------------------------------

        if status.get(
            "last_error"
        ):

            response["last_error"] = (
                status.get(
                    "last_error"
                )
            )

        return response

    except Exception as error:

        logger.error(
            f"[INGESTION] Failed to retrieve status: "
            f"{error}"
        )

        return {
            "processed":
                0,

            "failed":
                0,

            "worker_running":
                False,

            "dataset_rows_processed":
                0,

            "ingestion": {
                "status":
                    "unavailable",

                "processed":
                    0,

                "failed":
                    0,

                "dataset_rows_processed":
                    0
            },

            "error": (
                "Ingestion status temporarily "
                "unavailable."
            )
        }