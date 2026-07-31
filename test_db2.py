import dns.resolver
dns.resolver.default_resolver = dns.resolver.Resolver(configure=False)
dns.resolver.default_resolver.nameservers = ['8.8.8.8']

from pymongo import MongoClient
import certifi
import json

uri = "mongodb+srv://admin_db_user:admin%40123@cluster0.drmnlav.mongodb.net/?appName=Cluster0"
client = MongoClient(uri, tlsCAFile=certifi.where())
db = client["aisaconnect_db_v5"]

pipeline = [
    {"$group": {"_id": "$channel", "count": {"$sum": 1}}}
]
counts = list(db["api_message"].aggregate(pipeline))

with open("channel_counts.json", "w", encoding="utf-8") as f:
    json.dump(counts, f, indent=2)
print("Saved to channel_counts.json")
