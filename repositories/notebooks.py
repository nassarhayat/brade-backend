from bson import ObjectId
from models.notebook import NotebookModel
from pymongo.mongo_client import MongoClient
from typing import Optional
from repositories.blocks import add_block_to_blocks_repo

def get_notebook_repo(notebook_id: str, client: MongoClient):
    notebooks_collection = client["brade_dev"]["notebooks"]

    pipeline = [
        {"$match": {"_id": ObjectId(notebook_id)}},
        {"$addFields": {"id": {"$toString": "$_id"}}},
        {"$addFields": {"thread_items": {"$ifNull": ["$thread_items", []]}}},
        # Extract blockIds from thread_items where blockId is not None
        {"$addFields": {
            "blockIds": {
                "$filter": {
                    "input": {
                        "$map": {
                            "input": "$thread_items",
                            "as": "item",
                            "in": {
                                "$cond": [
                                    {"$and": [
                                        {"$ne": ["$$item.blockId", None]},
                                        {"$ne": ["$$item.blockId", ""]}  # Also handle empty strings if necessary
                                    ]},
                                    {"$toObjectId": "$$item.blockId"},
                                    None
                                ]
                            }
                        }
                    },
                    "as": "id",
                    "cond": {"$ne": ["$$id", None]}
                }
            }
        }},
        # Perform a lookup to join blocks based on blockIds
        {"$lookup": {
            "from": "blocks",
            "localField": "blockIds",
            "foreignField": "_id",
            "as": "blocks"
        }},
        {
            "$project": {
                "_id": 0,
                "id": 1,
                "title": 1,
                "thread_items": {
                    "$map": {
                        "input": "$thread_items",
                        "as": "item",
                        "in": {
                            "$mergeObjects": [
                                "$$item",
                                {"id": {"$toString": "$$item._id"}},
                                {
                                    "block": {
                                        "$cond": [
                                            {"$and": [
                                                {"$ne": ["$$item.blockId", None]},
                                                {"$ne": ["$$item.blockId", ""]}
                                            ]},
                                            {
                                                "$arrayElemAt": [
                                                    {
                                                        "$filter": {
                                                            "input": "$blocks",
                                                            "as": "block",
                                                            "cond": {
                                                                "$eq": [
                                                                    "$$block._id",
                                                                    {"$toObjectId": "$$item.blockId"}
                                                                ]
                                                            }
                                                        }
                                                    },
                                                    0
                                                ]
                                            },
                                            None
                                        ]
                                    }
                                }
                            ]
                        }
                    }
                }
            }
        }
    ]

    result = list(notebooks_collection.aggregate(pipeline))

    if result:
        return result[0]
    else:
        return {"error": "Document not found"}

def get_notebooks_repo(filter_by: str, client):
  collection = client["brade_dev"]["notebooks"]
  pipeline = [
    {"$match": {"title": {"$regex": filter_by, "$options": "i"}}} if filter_by else {"$match": {}},
    {"$addFields": {"id": {"$toString": "$_id"}}},
    {"$project": {"_id": 0}}
  ]
  notebooks = list(collection.aggregate(pipeline))
  return notebooks

def create_notebook_repo(notebook: NotebookModel, client: MongoClient):
  collection = client["brade_dev"]["notebooks"]
  insert_result = collection.insert_one(notebook.model_dump(by_alias=True))
  notebook.id = str(insert_result.inserted_id)
  return notebook

def add_thread_item_to_notebook_repo(
  notebook_id: str,
  thread_item: dict,
  block_item: Optional[dict],
  client: MongoClient
):
  collection = client["brade_dev"]["notebooks"]
  
  block_id = None
  if block_item:
    block_id = add_block_to_blocks_repo(block_item, client)
    if block_id:
      thread_item.blockId = str(block_id)
    else:
      return {"success": False, "message": "Failed to store block"}
          
  result = collection.update_one(
      {"_id": ObjectId(notebook_id)},
      {"$push": {"thread_items": thread_item.model_dump(by_alias=True)}}
  )
  if result.modified_count == 1:
      return {"success": True, "message": "Thread item added successfully"}
  else:
      return {"success": False, "message": "Failed to add thread item or notebook not found"}