from typing import List
from bson import ObjectId
from models.notebook import ThreadModel
from pymongo.mongo_client import MongoClient
from bson.objectid import ObjectId

def get_thread_repo(thread_id: str, client: MongoClient):
  collection = client["brade_dev"]["threads"]
  find_result = collection.find_one({"_id": ObjectId(thread_id)})
  if find_result:
    find_result['id'] = str(find_result['_id'])
    del find_result['_id']
    return find_result
  else:
    return {"error": "Thread not found"}

def get_threads_repo(thread_ids: List[str], client):
  collection = client["brade_dev"]["threads"]
  if thread_ids:
    threads = list(collection.find({"_id": {"$in": thread_ids}}))
  else:
    threads = list(collection.find())
  return threads

def create_thread_repo(thread: ThreadModel, client: MongoClient):
  collection = client["brade_dev"]["threads"]
  insert_result = collection.insert_one(thread.model_dump(by_alias=True))
  thread.id = str(insert_result.inserted_id)
  return thread