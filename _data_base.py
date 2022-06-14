from dotenv import load_dotenv, find_dotenv
import os
from numpy import insert
from pymongo import MongoClient

password = os.environ.get("MONGODB_PWD")

connection_string = f"mongodb+srv://Kararu:{password}@cryptoapp.zhsbqpe.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(connection_string)

dbs = client.list_database_names()
user = client.user_data
collections = user.list_collection_names()
print(dbs)


def addDBS():
    collection = user.passwords

    test_doc = {"name": "kararu", "password": "Kao1st99"}
    insert_id = collection.insert_one(test_doc).inserted_id
    print(insert_id)


addDBS()
