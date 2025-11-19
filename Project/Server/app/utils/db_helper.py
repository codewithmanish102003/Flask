from pymongo import MongoClient


def get_db_connection(mongo_uri):
    """Create and return a MongoDB database connection."""
    client = MongoClient(mongo_uri)
    db = client.get_default_database()
    return db