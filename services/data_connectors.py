from models.data_connector import DataConnectorModel
from repositories.data_connectors import add_data_connector_to_repo, get_data_connectors_repo
from schemas.data_connector import DataConnectorCreate
import hashlib
from uuid import uuid4

async def encrypt_password(password: str) -> str:
    salt = "secret_salt" 
    return hashlib.sha256((password + salt).encode()).hexdigest()
  
async def create_data_connector(data: DataConnectorCreate, user_id: str, client):
    if data.type == "sql_database":
        if not all([data.db_host, data.db_name, data.db_user, data.db_password, data.db_port]):
            raise ValueError("All fields for SQL database are required")
        data.db_password = await encrypt_password(data.db_password)
    
    connector_data = data.dict()
    connector_data["user_id"] = user_id
    connector_data["id"] = str(uuid4())

    connector_model = DataConnectorModel(**connector_data)
    inserted_connector = add_data_connector_to_repo(connector_model, client)
    if inserted_connector is None:
        raise Exception("Failed to save connector to database")
    return inserted_connector


async def get_data_connectors(user_id: str, client):
    connectors = get_data_connectors_repo(user_id, client)
    if not connectors:
        return []
    return connectors
