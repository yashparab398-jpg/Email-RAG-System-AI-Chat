from fastapi import APIRouter

from app.database.mongodb import emails_collection


router = APIRouter(
    prefix="/insights",
    tags=["Insights"]
)


@router.get("/high-risk")
def high_risk_emails():

    risk_keywords = [
        "legal",
        "lawsuit",
        "investigation",
        "risk",
        "fraud",
        "sec",
        "compliance",
        "subpoena"
    ]

    results = []

    try:

        emails = emails_collection.find(
            {},
            {
                "_id": 0,
                "message_id": 1,
                "subject": 1,
                "from": 1,
                "date": 1,
                "body": 1
            },
            batch_size=500
        ).max_time_ms(10000)

        for email in emails:

            body = str(
                email.get("body") or ""
            ).lower()

            for keyword in risk_keywords:

                if keyword in body:

                    results.append(
                        {
                            "message_id":
                                email.get(
                                    "message_id"
                                ),

                            "subject":
                                email.get(
                                    "subject"
                                ),

                            "from":
                                email.get(
                                    "from"
                                ),

                            "date":
                                email.get(
                                    "date"
                                ),

                            "matched_keyword":
                                keyword
                        }
                    )

                    break

                # We only need enough results
                # for the frontend.
                if len(results) >= 20:
                    break

            if len(results) >= 20:
                break

    except Exception as error:

        print(
            "[RISK] MongoDB query failed:",
            error
        )

        return {
            "count": 0,
            "emails": [],
            "error":
                "Risk data is temporarily unavailable."
        }

    return {
        "count": len(results),
        "emails": results
    }