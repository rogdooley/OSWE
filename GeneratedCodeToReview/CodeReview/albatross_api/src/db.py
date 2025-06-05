from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client.albatross
users = db.users

def get_user_by_query(query):
    return users.find_one(query)
