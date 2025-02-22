
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os

MONGODB_URI = os.environ.get("MONGODB_URI")
print(MONGODB_URI)
# Create a new client and connect to the server
client = MongoClient(MONGODB_URI, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)
