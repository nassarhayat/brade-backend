from repositories.blocks import update_block_repo
from pymongo.mongo_client import MongoClient

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
      user_id (str): The ID of the user making the request.
      client (MongoClient): The MongoDB client instance.

  Returns:
      dict: The updated block information.
  """
  # Validate input
  if not notebook_id or not block_id:
      raise ValueError("Notebook ID and Block ID are required.")

  success = update_block_repo(
      block_id=block_id,
      client=client,
  )

  if not success:
      raise RuntimeError(f"Failed to update block with ID {block_id}.")

  return {"notebookId": notebook_id, "blockId": block_id}
