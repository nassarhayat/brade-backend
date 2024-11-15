import uuid
import json
from typing import Optional
from models.notebook import NotebookModel
from models.thread import ThreadItemModel, UserType
from models.block import BlockModel, BlockType, LayoutItem
from services.agents import run_swarm
from repositories.notebooks import get_notebooks_repo, get_notebook_repo, \
  create_notebook_repo, add_thread_item_to_notebook_repo
from repositories.blocks import update_block_repo, get_blocks_repo
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
  add_thread_item_to_notebook_repo(notebook_id, thread_item, None, client)
  
  agent_response = run_swarm(thread_item_data.content)
  response_content = ""

  async def collect_and_save_response():
      nonlocal response_content
      block_item = None
      async for chunk in agent_response:
        if chunk and chunk.strip():
          try:
            chunk_dict = json.loads(chunk)
            content = chunk_dict.get("content", "")            
            if chunk_dict.get("role") == "tool":
              tool_type = chunk_dict.get("toolType")
              print("Tool type:", tool_type)
              if tool_type == "chart":
                block_type = BlockType.chart
              elif tool_type == "stacked-chart":
                block_type = BlockType.stacked_chart
              elif tool_type == "line-chart":
                block_type = BlockType.line_chart
              elif tool_type == "table":
                block_type = BlockType.table
              else:
                block_type = BlockType.number
              block_item = BlockModel(
                  blockType=block_type,
                  data=content,
                  notebookId=notebook_id
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
          )
          add_thread_item_to_notebook_repo(
            notebook_id,
            response_thread_item,
            block_item,
            client
          )

  return collect_and_save_response()

def add_block_to_notebook_service(
  notebook_id: str,
  block_id: str,
  user_id: str,
  client: MongoClient
):
  """
  Adds or updates a block in a notebook by updating its layout.

  Args:
      notebook_id (str): The ID of the notebook.
      block_id (str): The ID of the block.
      layout_item (LayoutItem): The new layout values for the block.
      user_id (str): The ID of the user making the request.
      client (MongoClient): The MongoDB client instance.

  Returns:
      dict: The updated block information.
  """
  # Validate input
  if not notebook_id or not block_id:
      raise ValueError("Notebook ID and Block ID are required.")

  layout_item = LayoutItem(
    i='index1',
    x=15,
    y=25,
    w=5,
    h=4,
    minW=2,
    minH=2,
    static=False,
  )
  # Call repository function to update block
  success = update_block_repo(
      block_id=block_id,
      layout=layout_item.dict(by_alias=True),
      client=client,
  )

  if not success:
      raise RuntimeError(f"Failed to update block with ID {block_id}.")

  return {"notebookId": notebook_id, "blockId": block_id, "layout": layout_item.model_dump(by_alias=True)}

def get_blocks_for_notebook_service(
  notebook_id: str, 
  client: MongoClient
):
  response = get_blocks_repo(notebook_id, client)
  return response