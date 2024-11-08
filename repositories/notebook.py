from bson import ObjectId
from models.notebook import NotebookModel
from pymongo.mongo_client import MongoClient
from bson.objectid import ObjectId

def get_notebook_repo(notebook_id: str, client: MongoClient):
  collection = client["brade_dev"]["notebooks"]
  pipeline = [
      {"$match": {"_id": ObjectId(notebook_id)}},
      {"$addFields": {"id": {"$toString": "$_id"}}},
      {
          "$project": {
              "_id": 0,  # Exclude the original _id field
              "id": 1,   # Include the new id field as a string
              "title": 1,  # Include other top-level fields as needed
              "thread_items": {
                  "$map": {
                      "input": "$thread_items",
                      "as": "item",
                      "in": {
                          "$mergeObjects": [
                              "$$item",
                              {"id": {"$toString": "$$item._id"}}
                          ]
                      }
                  }
              }
          }
      }
  ]
  
  result = list(collection.aggregate(pipeline))
  
  if result:
      return result[0]
  else:
      return {"error": "Document not found"}
  # find_result = collection.find_one({"_id": ObjectId(notebook_id)})
  # if find_result:
  #   find_result['id'] = str(find_result['_id'])
  #   del find_result['_id']
  #   return find_result
  # else:
  #   return {"error": "Document not found"}

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
  client: MongoClient
):
  collection = client["brade_dev"]["notebooks"]
  result = collection.update_one(
      {"_id": ObjectId(notebook_id)},
      {"$push": {"thread_items": thread_item.model_dump(by_alias=True)}}
  )
  if result.modified_count == 1:
      return {"success": True, "message": "Thread item added successfully"}
  else:
      return {"success": False, "message": "Failed to add thread item or notebook not found"}