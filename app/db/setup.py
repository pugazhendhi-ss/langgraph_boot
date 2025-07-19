from pymongo import MongoClient

from app.config.settings import DB_URL, DB_NAME


def get_db():
    client = MongoClient(DB_URL)
    database = client[DB_NAME]
    try:
        yield database
    finally:
        client.close()
