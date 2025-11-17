import os
from pymongo import MongoClient


def get_db(mongo_uri=None):
    if mongo_uri is None:
        mongo_uri = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/flask_modular_app')
    client = MongoClient(mongo_uri)
    db_name = mongo_uri.split('/')[-1]
    return client[db_name]
