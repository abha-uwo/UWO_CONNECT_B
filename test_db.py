import dns.resolver
dns.resolver.default_resolver = dns.resolver.Resolver(configure=False)
dns.resolver.default_resolver.nameservers = ['8.8.8.8']

from pymongo import MongoClient
import certifi
import json
import sys

uri = "mongodb+srv://admin_db_user:admin%40123@cluster0.drmnlav.mongodb.net/?appName=Cluster0"
client = MongoClient(uri, tlsCAFile=certifi.where())
db = client["aisaconnect_db_v5"]

messages = db["api_message"].find().sort("created_at", -1).limit(50)
output = []
for m in messages:
    output.append({
        "id": str(m.get("_id")),
        "channel": m.get("channel"),
        "from": m.get("from_address"),
        "to": m.get("to_address"),
        "type": m.get("message_type"),
        "body_len": len(m.get("body", "")) if m.get("body") else 0
    })

with open("messages_output.json", "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2)
print("Saved to messages_output.json")
