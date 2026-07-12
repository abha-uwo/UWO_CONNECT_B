import pymongo
import os
from dotenv import load_dotenv

load_dotenv()
client = pymongo.MongoClient(os.getenv('MONGODB_URI'))
db = client[os.getenv('MONGODB_DB_NAME')]

print('--- User details ---')
for u in db['api_user'].find():
    print(f"ID: {u['_id']}, Username: {u.get('username')}, Role: {u.get('role')}, Status: {u.get('status')}")
