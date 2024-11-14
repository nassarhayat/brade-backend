from typing import List
from bson import ObjectId
from models.block import BlockModel
from pymongo.mongo_client import MongoClient

def add_block_to_blocks_repo(block: BlockModel, client: MongoClient):
    collection = client["brade_dev"]["blocks"]
    result = collection.insert_one(block.model_dump(by_alias=True))
    if result.inserted_id:
        return str(result.inserted_id)
    else:
        return None