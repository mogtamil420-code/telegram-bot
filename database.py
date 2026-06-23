from pymongo import MongoClient
from config import MONGO_URL

client = MongoClient(MONGO_URL)
db = client["autofilter"]

files = db["files"]
users = db["users"]
settings = db["settings"]
