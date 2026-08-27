from app.ingestion.ingest import (
    read_email_batches,
    process_batch,
)

from app.database.mongodb import (
    emails_collection,
)


TARGET = 20000


def main():

    processed = emails_collection.count_documents({})

    print(
        f"Already in MongoDB: {processed}"
    )

    batches = read_email_batches()

    for batch in batches:

        if processed >= TARGET:

            break

        remaining = TARGET - processed

        if len(batch) > remaining:

            batch = batch.head(remaining)

        result = process_batch(batch)

        processed += result["parsed"]

        print(
            f"Imported: {processed}/{TARGET}"
        )

    print("Finished.")


if __name__ == "__main__":

    main()