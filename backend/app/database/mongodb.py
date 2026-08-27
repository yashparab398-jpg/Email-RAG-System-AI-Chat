from pymongo import MongoClient
from pymongo.errors import PyMongoError


MONGO_URI = "mongodb://127.0.0.1:27017"

DATABASE_NAME = "enron_email_intelligence"


# =========================================================
# MONGODB CLIENT
# =========================================================

client = MongoClient(
    MONGO_URI,
    serverSelectionTimeoutMS=5000,
    connectTimeoutMS=5000,
    socketTimeoutMS=30000,
)


# =========================================================
# DATABASE
# =========================================================

db = client[DATABASE_NAME]


# =========================================================
# COLLECTIONS
# =========================================================

emails_collection = db["emails"]

failed_collection = db["failed_records"]

ingestion_collection = db["ingestion_status"]


# =========================================================
# DATABASE ACCESS
# =========================================================

def get_database():
    return db


# =========================================================
# CONNECTION CHECK
# =========================================================

def check_mongodb():

    try:

        client.admin.command("ping")

        print(
            "[MONGODB] Connection successful"
        )

        return True

    except PyMongoError as error:

        print(
            "[MONGODB] Connection failed:",
            repr(error)
        )

        return False