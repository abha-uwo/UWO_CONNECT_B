import pymongo
import os
from dotenv import load_dotenv

load_dotenv()
client = pymongo.MongoClient(os.getenv('MONGODB_URI'))
db = client[os.getenv('MONGODB_DB_NAME')]

# Delete all clients where user_id is None (orphaned clients)
result = db['api_client'].delete_many({'user_id': None})
print(f"Deleted {result.deleted_count} orphaned clients.")

print('--- Remaining Clients ---')
for c in db['api_client'].find():
    print(f"ID: {c['_id']}, Name: {c.get('business_name')}, User ID: {c.get('user_id')}")
