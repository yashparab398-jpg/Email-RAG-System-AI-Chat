from collections import Counter

from fastapi import APIRouter

from app.database.mongodb import emails_collection


router = APIRouter(
    prefix="/insights",
    tags=["Insights"]
)


# =========================================================
# CONFIGURATION
# =========================================================

HUBS_SAMPLE_SIZE = 10000


# =========================================================
# CACHE
# =========================================================

_hubs_cache = None


# =========================================================
# HELPERS
# =========================================================

def normalize_recipients(value):

    if isinstance(value, list):

        values = value

    elif isinstance(value, str):

        values = value.split(",")

    else:

        values = []

    return [
        str(recipient).strip()
        for recipient in values
        if str(recipient).strip()
    ]


# =========================================================
# HUBS
# =========================================================

@router.get("/hubs")
def hubs():

    global _hubs_cache

    if _hubs_cache is not None:
        return _hubs_cache

    people = Counter()
    connections = Counter()

    try:

        # -------------------------------------------------
        # BOUNDED READ
        # -------------------------------------------------

        emails = (
            emails_collection
            .find(
                {},
                {
                    "_id": 0,
                    "from": 1,
                    "to": 1
                }
            )
            .limit(HUBS_SAMPLE_SIZE)
            .max_time_ms(5000)
        )

        # -------------------------------------------------
        # PROCESS EMAILS
        # -------------------------------------------------

        for email in emails:

            sender = email.get("from")

            if not sender:
                continue

            sender = str(sender).strip()

            if not sender:
                continue

            recipients = normalize_recipients(
                email.get("to")
            )

            # ---------------------------------------------
            # SENDER
            # ---------------------------------------------

            people[sender] += 1

            # ---------------------------------------------
            # RECIPIENTS + CONNECTIONS
            # ---------------------------------------------

            for recipient in recipients:

                people[recipient] += 1

                if sender == recipient:
                    continue

                connections[
                    (sender, recipient)
                ] += 1

        # -------------------------------------------------
        # TOP PEOPLE
        # -------------------------------------------------

        top_people = people.most_common(20)

        allowed_people = {
            person
            for person, _ in top_people
        }

        # -------------------------------------------------
        # NODES
        # -------------------------------------------------

        nodes = [
            {
                "id": person,
                "count": count
            }
            for person, count in top_people
        ]

        # -------------------------------------------------
        # EDGES
        # -------------------------------------------------

        edges = []

        for (
            sender,
            recipient
        ), count in connections.items():

            if (
                sender not in allowed_people
                or recipient not in allowed_people
            ):
                continue

            edges.append(
                {
                    "source": sender,
                    "target": recipient,
                    "count": count
                }
            )

        edges.sort(
            key=lambda edge: edge["count"],
            reverse=True
        )

        edges = edges[:60]

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------

        _hubs_cache = {
            "communication_hubs": top_people,
            "nodes": nodes,
            "edges": edges,
            "sample_size": HUBS_SAMPLE_SIZE
        }

        print(
            "[HUBS] Successfully calculated.",
            flush=True
        )

        return _hubs_cache

    except Exception as error:

        print(
            "[HUBS] MongoDB query failed:",
            repr(error),
            flush=True
        )

        return {
            "communication_hubs": [],
            "nodes": [],
            "edges": [],
            "error":
                "Communication hub data is temporarily unavailable."
        }