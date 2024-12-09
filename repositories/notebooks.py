from bson import ObjectId
from models.notebook import NotebookModel
from pymongo.mongo_client import MongoClient

def get_notebook_repo(notebook_id: str, client: MongoClient):
    notebooks_collection = client["brade_dev"]["notebooks"]

    pipeline = [
        # Match the specific notebook
        {"$match": {"_id": ObjectId(notebook_id)}},

        # Add the root-level id field
        {"$addFields": {"id": {"$toString": "$_id"}}},

        # Lookup blocks
        {
            "$lookup": {
                "from": "blocks",
                "localField": "_id",
                "foreignField": "notebookId",
                "as": "blocks"
            }
        },

        # Project the final structure
        {
            "$project": {
                "_id": 0,
                "id": 1,
                "title": 1,
                "blocks": {
                    "$map": {
                        "input": "$blocks",
                        "as": "block",
                        "in": {
                            "$mergeObjects": [
                                {"id": {"$toString": "$$block._id"}},
                                {"notebookId": {"$toString": "$$block.notebookId"}},
                                {
                                    "$arrayToObject": {
                                        "$filter": {
                                            "input": {"$objectToArray": "$$block"},
                                            "as": "field",
                                            "cond": {"$and": [
                                                {"$ne": ["$$field.k", "_id"]},
                                                {"$ne": ["$$field.k", "notebookId"]}
                                            ]}
                                        }
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