from app.database.mongodb import emails_collection


def search_emails(question):

    question = question.lower()

    keywords = question.split()

    results = []

    emails = emails_collection.find(
        {},
        {
            "raw_body": 0
        }
    )

    for email in emails:

        searchable_text = " ".join(
            [
                str(email.get("subject", "")),
                str(email.get("body", "")),
                str(email.get("from", "")),
                str(email.get("to", ""))
            ]
        ).lower()

        for keyword in keywords:

            if keyword in searchable_text:

                email["_id"] = str(email["_id"])

                results.append(email)

                break

    return results[:10]