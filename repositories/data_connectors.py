from pymongo import MongoClient
from models.data_connector import DataConnectorModel

def add_data_connector_to_repo(connector: DataConnectorModel, client: MongoClient):
    collection = client["brade_dev"]["data_connectors"]
    
    connector_data = connector.model_dump(by_alias=True, exclude_none=True)
    
    result = collection.insert_one(connector_data)
    if result.inserted_id:
        connector_data["id"] = str(result.inserted_id)
        connector_data.pop("_id", None)
        return connector_data
    else:
        return None

def get_data_connectors_repo(user_id: str, client: MongoClient):
    collection = client["brade_dev"]["data_connectors"]
    connectors = list(collection.find({"user_id": user_id}))
    
    for connector in connectors:
        connector["id"] = str(connector.pop("_id", None))
    return connectors