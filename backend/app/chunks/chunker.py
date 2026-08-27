import uuid


CHUNK_SIZE = 500


def split_text(text, chunk_size=CHUNK_SIZE):

    if not text:
        return []

    words = text.split()

    chunks = []

    for i in range(0, len(words), chunk_size):

        chunk = " ".join(
            words[i:i + chunk_size]
        )

        chunks.append(chunk)

    return chunks


def create_chunks(email_document):

    text_chunks = split_text(
        email_document.get(
            "clean_body",
            ""
        )
    )

    documents = []

    for index, chunk_text in enumerate(text_chunks):

        chunk = {
            "chunk_id": str(
                uuid.uuid4()
            ),
            "email_id": str(
                email_document.get(
                    "_id",
                    ""
                )
            ),
            "subject": email_document.get(
                "subject"
            ),
            "from": email_document.get(
                "from"
            ),
            "to": email_document.get(
                "to"
            ),
            "cc": email_document.get(
                "cc"
            ),
            "date": email_document.get(
                "date"
            ),
            "chunk_text": chunk_text,
            "chunk_index": index,
            "metadata": {
                "folder": email_document.get(
                    "folder_path"
                ),
                "mailbox_owner": email_document.get(
                    "mailbox_owner"
                ),
            },
        }

        documents.append(chunk)

    return documents