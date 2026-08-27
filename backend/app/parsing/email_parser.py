import email
from email import policy
from email.parser import Parser


def parse_email(raw_email, file_path):
    try:
        parsed = Parser(policy=policy.default).parsestr(str(raw_email))

        sender = parsed.get("From")

        recipients = parsed.get("To")

        cc = parsed.get("Cc")

        bcc = parsed.get("Bcc")

        subject = parsed.get("Subject")

        message_id = parsed.get("Message-ID")

        date = parsed.get("Date")

        body = ""

        if parsed.is_multipart():

            for part in parsed.walk():

                if part.get_content_type() == "text/plain":

                    body += part.get_content()

        else:

            body = parsed.get_body(
                preferencelist=("plain",)
            )

            if body:

                body = body.get_content()

            else:

                body = parsed.get_payload()

        return {
            "message_id": message_id,
            "date": date,
            "from": sender,
            "to": recipients,
            "cc": cc,
            "bcc": bcc,
            "subject": subject,
            "body": body,
            "folder_path": file_path,
            "mailbox_owner": str(file_path).split("/")[0],
            "raw_body": raw_email,
            "status": "parsed"
        }

    except Exception as error:

        return {
            "error": str(error),
            "raw_body": raw_email,
            "folder_path": file_path,
            "status": "failed"
        }