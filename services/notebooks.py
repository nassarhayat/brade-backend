import uuid
import json
from typing import Optional
from models.notebook import NotebookModel
from models.thread import ThreadItemModel, UserType
from models.block import BlockModel, BlockType
from services.agents import run_swarm
from repositories.notebook import get_notebooks_repo, get_notebook_repo, \
  create_notebook_repo, add_thread_item_to_notebook_repo
from pymongo.mongo_client import MongoClient

def get_notebooks_service(filter_by: Optional[str], client: MongoClient):
  response = get_notebooks_repo(filter_by, client)
  return response

def get_notebook_service(id: str, client: MongoClient):
  response = get_notebook_repo(id, client)
  return response

def create_notebook_service(title: str, client: MongoClient):
  print(title)
  notebook = NotebookModel(title=title)
  new_notebook = create_notebook_repo(notebook, client)
  return new_notebook

def add_thread_item_service(
  notebook_id: str,
  thread_item_data: ThreadItemModel,
  user_id: str,
  client: MongoClient
):
  thread_item = ThreadItemModel(
    content=thread_item_data.content,
    userType=UserType.user,
    userId=user_id
  )
  # notebook = add_thread_item_to_notebook_repo(notebook_id, thread_item, client)
  # agent_response = run_swarm(thread_item_data.content)
  # return agent_response
  add_thread_item_to_notebook_repo(notebook_id, thread_item, client)
  
  agent_response = run_swarm(thread_item_data.content)
  response_content = ""

  async def collect_and_save_response():
      nonlocal response_content
      
      async for chunk in agent_response:
        if chunk and chunk.strip():
          try:
            chunk_dict = json.loads(chunk)
            content = chunk_dict.get("content", "")            
            if chunk_dict.get("role") == "tool":
              tool_type = chunk_dict.get("toolType")
              print("Tool type:", tool_type)
              block = BlockModel(
                  blockType=BlockType.chart,
                  data=content
              )
              content = ""
              # continue

            if isinstance(content, str):
              print("Content:", content)
              print("CHUNK", type(chunk), chunk)
              
              response_content += content
              yield chunk
          except json.JSONDecodeError:
            print("Invalid JSON chunk:", repr(chunk))
            continue

      if response_content:
          response_thread_item = ThreadItemModel(
              content=response_content,
              userType=UserType.assistant,
              block=block
          )
          add_thread_item_to_notebook_repo(notebook_id, response_thread_item, client)

  return collect_and_save_response()
