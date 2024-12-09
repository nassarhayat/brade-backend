from repositories.notebooks import get_notebooks_repo
from typing import Optional
from pymongo.mongo_client import MongoClient

def get_notebooks_service(filter_by: Optional[str], client: MongoClient):
  response = get_notebooks_repo(filter_by, client)
  return response
