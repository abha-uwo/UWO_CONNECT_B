import pymongo
import os
from dotenv import load_dotenv

load_dotenv()
client = pymongo.MongoClient(os.getenv('MONGODB_URI'))
db = client[os.getenv('MONGODB_DB_NAME')]

# Delete all users whose email is not admin@uwo24.com
result = db['api_user'].delete_many({'email': {'$ne': 'admin@uwo24.com'}})
print(f'Deleted {result.deleted_count} users.')

print('--- Remaining Users ---')
for u in db['api_user'].find({}, {'username': 1, 'email': 1, 'role': 1}):
    print(u)
