import pymongo
import os
from dotenv import load_dotenv

load_dotenv()
client = pymongo.MongoClient(os.getenv('MONGODB_URI'))
db = client[os.getenv('MONGODB_DB_NAME')]

print('--- All Clients ---')
for c in db['api_client'].find():
    print(f"ID: {c['_id']}, Name: {c.get('business_name')}, User ID: {c.get('user_id')}")
