import os
import pymongo
from pymongo import MongoClient
import json

connection_string = os.getenv("MONGO_API_KEY")

client = MongoClient(connection_string)

db = client['farmer_assessment_db']

# Access your collection
collection_crops = db['crops']
collection_applications = db['applications']
collection_assesments = db['assesments']
collection_documents = db['documents']
collection_farmers = db['farmers']
collection_harvest_logs = db['harvest_logs']
collection_invetory = db['invetory']
collection_orders = db['orders']
collection_tasks = db['tasks']
collection_weather = db["weather_logs"]

import datetime

from bson import ObjectId

def serialize_datetime(obj):
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    if isinstance(obj, ObjectId):
        return str(obj)
    raise TypeError("Type not serializable")

# documents = collection_crops.find()
# for doc in documents:
#     print(json.dumps(doc, indent=4, default=serialize_datetime))

# print("----------------------------------------------------------------------")

# query = {
#     "estimated_yield": {"$gte": 50},
#     "crop_name": "Porumb"
# }

# documents = collection_crops.find(query)

# for doc in documents:
#     print(json.dumps(doc, indent=4, default=serialize_datetime))

# print("----------------------------------------------------------------------")

# # Query for documents with notes = "Intense work"
# query = {
#     "notes": "Intensive work"
# }

# # Get the count
# count = collection_harvest_logs.count_documents(query)
# print(f"Found {count} documents with 'Intense work' notes")

# # Retrieve and display the documents
# documents = collection_harvest_logs.find(query)
# for doc in documents:
#     print(json.dumps(doc, indent=4, default=serialize_datetime))