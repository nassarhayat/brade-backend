from repositories.notebooks import get_notebook_repo
from pymongo.mongo_client import MongoClient

def get_notebook_service(id: str, client: MongoClient):
  response = get_notebook_repo(id, client)
  return response