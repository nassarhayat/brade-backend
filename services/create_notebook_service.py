from repositories.notebooks import create_notebook_repo
from pymongo.mongo_client import MongoClient
from models.notebook import NotebookModel

def create_notebook_service(title: str, client: MongoClient):
  print(title)
  notebook = NotebookModel(title=title)
  new_notebook = create_notebook_repo(notebook, client)
  return new_notebook
