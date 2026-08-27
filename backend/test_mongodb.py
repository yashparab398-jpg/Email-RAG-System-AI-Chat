from app.ingestion.ingest import (
    read_email_batches,
    process_batch,
)


def main():

    batch = next(
        read_email_batches()
    )

    result = process_batch(
        batch
    )

    print(result)


if __name__ == "__main__":

    main()