from fastapi import APIRouter

from app.database.mongodb import (
    emails_collection,
    ingestion_collection,
)


router = APIRouter(
    prefix="/insights",
    tags=["Insights"]
)


# =========================================================
# CACHE
# =========================================================

_summary_cache = None
_network_cache = None
_topics_cache = None


# =========================================================
# CONFIGURATION
# =========================================================

# Keep analytics deliberately small.
# The goal is fast UI response, not a full 692k-email scan.
ANALYTICS_SAMPLE_SIZE = 5000


# =========================================================
# HELPERS
# =========================================================

def get_current_email_count():

    try:

        status = ingestion_collection.find_one(
            {},
            {
                "_id": 0,
                "status": 1,
                "processed": 1,
            }
        )

        if status:

            ingestion_status = str(
                status.get("status", "")
            ).lower()

            processed = int(
                status.get("processed", 0) or 0
            )

            if ingestion_status == "processing":

                return processed

    except Exception as error:

        print(
            "[INSIGHTS] Ingestion status error:",
            repr(error),
            flush=True
        )

    try:

        return int(
            emails_collection.estimated_document_count()
        )

    except Exception as error:

        print(
            "[INSIGHTS] Email count error:",
            repr(error),
            flush=True
        )

        return 0


def normalize_recipients(value):

    if isinstance(value, list):

        values = value

    elif isinstance(value, str):

        values = value.split(",")

    else:

        values = []

    return [
        str(value).strip()
        for value in values
        if str(value).strip()
    ]


# =========================================================
# SUMMARY
# =========================================================

@router.get("/summary")
def summary():

    global _summary_cache

    if _summary_cache is not None:
        return _summary_cache

    try:

        total_emails = get_current_email_count()

        sender_counts = {}
        recipient_counts = {}

        # -------------------------------------------------
        # ONE SMALL QUERY
        # -------------------------------------------------

        cursor = emails_collection.find(
            {},
            {
                "_id": 0,
                "from": 1,
                "to": 1,
            }
        ).limit(ANALYTICS_SAMPLE_SIZE)

        for email in cursor:

            # -----------------------------
            # SENDER
            # -----------------------------

            sender = email.get("from")

            if sender:

                sender = str(sender).strip()

                if sender:

                    sender_counts[sender] = (
                        sender_counts.get(sender, 0) + 1
                    )

            # -----------------------------
            # RECIPIENTS
            # -----------------------------

            for recipient in normalize_recipients(
                email.get("to")
            ):

                recipient_counts[recipient] = (
                    recipient_counts.get(recipient, 0) + 1
                )

        top_senders = [
            [
                sender,
                count
            ]
            for sender, count in sorted(
                sender_counts.items(),
                key=lambda item: item[1],
                reverse=True
            )[:10]
        ]

        top_recipients = [
            [
                recipient,
                count
            ]
            for recipient, count in sorted(
                recipient_counts.items(),
                key=lambda item: item[1],
                reverse=True
            )[:10]
        ]

        _summary_cache = {
            "total_emails": total_emails,
            "top_senders": top_senders,
            "top_recipients": top_recipients,
        }

        print(
            "[INSIGHTS/SUMMARY] Successfully calculated.",
            flush=True
        )

        return _summary_cache

    except Exception as error:

        print(
            "[INSIGHTS/SUMMARY] Error:",
            repr(error),
            flush=True
        )

        return {
            "total_emails": 0,
            "top_senders": [],
            "top_recipients": [],
            "error": "Summary data temporarily unavailable.",
        }


# =========================================================
# NETWORK
# =========================================================

@router.get("/network")
def network():

    global _network_cache

    if _network_cache is not None:
        return _network_cache

    try:

        communication_counts = {}

        cursor = emails_collection.find(
            {},
            {
                "_id": 0,
                "from": 1,
                "to": 1,
            }
        ).limit(ANALYTICS_SAMPLE_SIZE)

        for email in cursor:

            sender = email.get("from")

            if not sender:
                continue

            sender = str(sender).strip()

            if not sender:
                continue

            recipients = normalize_recipients(
                email.get("to")
            )

            for recipient in recipients:

                if sender == recipient:
                    continue

                key = (
                    sender,
                    recipient
                )

                communication_counts[key] = (
                    communication_counts.get(key, 0) + 1
                )

        top_pairs = sorted(
            communication_counts.items(),
            key=lambda item: item[1],
            reverse=True
        )[:20]

        communication_pairs = [
            [
                sender,
                recipient,
                count
            ]
            for (
                sender,
                recipient
            ), count in top_pairs
        ]

        _network_cache = {
            "communication_pairs": communication_pairs
        }

        print(
            "[INSIGHTS/NETWORK] Successfully calculated.",
            flush=True
        )

        return _network_cache

    except Exception as error:

        print(
            "[INSIGHTS/NETWORK] Error:",
            repr(error),
            flush=True
        )

        return {
            "communication_pairs": [],
            "error": "Network data temporarily unavailable.",
        }


# =========================================================
# TOPICS
# =========================================================

@router.get("/topics")
def topics():

    global _topics_cache

    if _topics_cache is not None:
        return _topics_cache

    keywords = [
        "energy",
        "trading",
        "legal",
        "contract",
        "deal",
        "investigation",
        "risk",
        "market",
    ]

    counts = {
        keyword: 0
        for keyword in keywords
    }

    try:

        cursor = emails_collection.find(
            {},
            {
                "_id": 0,
                "body": 1,
                "clean_body": 1,
            }
        ).limit(ANALYTICS_SAMPLE_SIZE)

        for email in cursor:

            body = str(
                email.get("clean_body")
                or email.get("body")
                or ""
            ).lower()

            if not body:
                continue

            for keyword in keywords:

                if keyword in body:

                    counts[keyword] += 1

        _topics_cache = counts

        print(
            "[INSIGHTS/TOPICS] Successfully calculated.",
            flush=True
        )

        return _topics_cache

    except Exception as error:

        print(
            "[INSIGHTS/TOPICS] Error:",
            repr(error),
            flush=True
        )

        return {
            keyword: 0
            for keyword in keywords
        }