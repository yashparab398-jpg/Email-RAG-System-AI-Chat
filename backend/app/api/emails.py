from fastapi import APIRouter

from app.database.mongodb import emails_collection

router = APIRouter(
    prefix="/emails",
    tags=["Emails"]
)


@router.get("")
def get_emails(limit: int = 20):

    emails = list(
        emails_collection.find(
            {},
            {
                "raw_body": 0
            }
        ).limit(limit)
    )

    for email in emails:
        email["_id"] = str(email["_id"])

    return emails


@router.get("/count")
def get_email_count():

    return {
        "total_emails": emails_collection.count_documents({})
    }


@router.get("/message/{message_id}")
def get_email_by_message_id(message_id: str):

    email = emails_collection.find_one(
        {
            "message_id": message_id
        }
    )

    if not email:

        return {
            "error": "Email not found"
        }

    email["_id"] = str(email["_id"])

    return email


@router.get("/{message_id}")
def get_email(message_id: str):

    email = emails_collection.find_one(
        {
            "message_id": message_id
        }
    )

    if not email:

        return {
            "error": "Email not found"
        }

    email["_id"] = str(email["_id"])

    return email