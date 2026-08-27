from collections import Counter
from email.utils import parsedate_to_datetime

from fastapi import APIRouter

from app.database.mongodb import emails_collection


router = APIRouter(
    prefix="/insights",
    tags=["Insights"]
)


# =========================================================
# CACHE
# =========================================================

_timeline_cache = None


# =========================================================
# CONFIGURATION
# =========================================================

TIMELINE_SAMPLE_SIZE = 10000


# =========================================================
# TIMELINE
# =========================================================

@router.get("/timeline")
def timeline():

    global _timeline_cache

    # -----------------------------------------------------
    # RETURN CACHE
    # -----------------------------------------------------

    if _timeline_cache is not None:
        return _timeline_cache

    monthly_counts = Counter()

    try:

        # -------------------------------------------------
        # BOUNDED READ
        # -------------------------------------------------

        cursor = (
            emails_collection
            .find(
                {},
                {
                    "_id": 0,
                    "date": 1
                }
            )
            .limit(TIMELINE_SAMPLE_SIZE)
            .max_time_ms(5000)
        )

        for email in cursor:

            date_value = email.get("date")

            if not date_value:
                continue

            try:

                if isinstance(
                    date_value,
                    str
                ):

                    date = parsedate_to_datetime(
                        date_value
                    )

                else:

                    continue

                month_key = date.strftime(
                    "%Y-%m"
                )

                monthly_counts[
                    month_key
                ] += 1

            except Exception:

                continue

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------

        result = {
            "timeline": dict(
                sorted(
                    monthly_counts.items()
                )
            ),
            "sample_size": TIMELINE_SAMPLE_SIZE
        }

        _timeline_cache = result

        print(
            "[TIMELINE] Successfully calculated.",
            flush=True
        )

        return result

    except Exception as error:

        print(
            "[TIMELINE] MongoDB query failed:",
            repr(error),
            flush=True
        )

        return {
            "timeline": {},
            "error":
                "Timeline data is temporarily unavailable."
        }