import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from typing import Generator
from dotenv import load_dotenv
load_dotenv()


mongodb_pw = os.getenv("MONGODB_PW")
uri = f"mongodb+srv://nassarhayat:{mongodb_pw}@cluster0.tshuf.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

client = MongoClient(uri, server_api=ServerApi('1'))
database = client["brade_dev"]
collection = database["notebooks"]

def get_mongo_client() -> Generator[MongoClient, None, None]:
  try:
    yield client
  finally:
    pass