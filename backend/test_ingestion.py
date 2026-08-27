from app.ingestion.ingest import read_email_batches


def main():
    batches = read_email_batches()

    first_batch = next(batches)

    print(first_batch.head())

    print()

    print("Rows loaded:", len(first_batch))


if __name__ == "__main__":
    main()