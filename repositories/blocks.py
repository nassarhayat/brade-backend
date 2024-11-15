from typing import List, Optional, Any
from bson import ObjectId
from models.block import BlockModel
from pymongo.mongo_client import MongoClient

def add_block_to_blocks_repo(block: BlockModel, client: MongoClient):
    collection = client["brade_dev"]["blocks"]
    block_data = block.model_dump(by_alias=True)
    if "notebookId" in block_data and isinstance(block_data["notebookId"], str):
        block_data["notebookId"] = ObjectId(block_data["notebookId"])

    result = collection.insert_one(block_data)
    if result.inserted_id:
        return str(result.inserted_id)
    else:
        return None

def get_blocks_repo(notebook_id: str, client: MongoClient):
    collection = client["brade_dev"]["blocks"]
    notebook_object_id = ObjectId(notebook_id)
    
    blocks = list(collection.find({
        "notebookId": notebook_object_id,
        "layout": { "$ne": None }
    }))
    
    for block in blocks:
        block["id"] = str(block.pop("_id"))
    
    return blocks

def update_block_repo(
    block_id: str,
    layout: Optional[Any],
    client: MongoClient,
) -> bool:
    """
    Updates the layout of a block by its block_id in the database.

    Args:
        block_id (str): The ID of the block to update.
        layout (Optional[Any]): The new layout to update in the block.
        client (MongoClient): The MongoDB client instance.

    Returns:
        bool: True if the update was successful, False otherwise.
    """
    collection = client["brade_dev"]["blocks"]

    # Convert block_id to ObjectId
    try:
        block_oid = ObjectId(block_id)
    except Exception as e:
        raise ValueError(f"Invalid block_id: {block_id}. Error: {e}")

    # Update the block's layout in the database
    result = collection.update_one({"_id": block_oid}, {"$set": {"layout": layout}})
    return result.modified_count > 0