from app.ingestion.ingest import read_email_batches
from app.parsing.email_parser import parse_email
from app.parsing.email_cleaner import clean_email


batch = next(read_email_batches())

email_row = batch.iloc[0]

parsed = parse_email(
    email_row["message"],
    email_row["file"]
)

cleaned = clean_email(
    parsed["body"]
)

print("ORIGINAL:")

print(parsed["body"])

print()

print("CLEANED:")

print(cleaned)