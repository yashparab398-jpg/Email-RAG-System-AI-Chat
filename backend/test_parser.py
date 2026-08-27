from app.ingestion.ingest import read_email_batches
from app.parsing.email_parser import parse_email


def main():

    batch = next(read_email_batches())

    first_email = batch.iloc[0]

    parsed = parse_email(
        first_email["message"],
        first_email["file"]
    )

    print(parsed)


if __name__ == "__main__":

    main()