from app.database.mongodb import (
    emails_collection,
)

from app.chunks.chunker import (
    create_chunks,
)


email_document = (
    emails_collection.find_one()
)

chunks = create_chunks(
    email_document
)

print(
    "Chunks:",
    len(chunks)
)

if chunks:

    print()

    print(
        chunks[0]
    )