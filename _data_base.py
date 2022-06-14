from dotenv import load_dotenv, find_dotenv
import os
from numpy import insert
from pymongo import MongoClient

password = os.environ.get("MONGODB_PWD")

connection_string = f"mongodb+srv://Kararu:{password}@cryptoapp.zhsbqpe.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(connection_string)

dbs = client.list_database_names()
user = client.user_data.passwords


def addDBS():

    test_doc = {"name": "Temmie", "password": "..."}
    insert_id = user.insert_one(test_doc).inserted_id
    print(insert_id)

def find(username):
    find = user.find_one({"name": username})
    print(find["password"])

find("kararu")
