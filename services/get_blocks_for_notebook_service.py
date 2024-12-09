from repositories.blocks import get_blocks_repo
from pymongo.mongo_client import MongoClient

def get_blocks_for_notebook_service(
  notebook_id: str, 
  client: MongoClient
):
  response = get_blocks_repo(notebook_id, client)
  return response