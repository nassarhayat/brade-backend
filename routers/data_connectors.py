from fastapi import APIRouter, Depends, HTTPException
from pydantic import ValidationError
from schemas.data_connector import DataConnectorCreate, DataConnectorResponse
from services.data_connectors import create_data_connector, get_data_connectors
from typing import List
from pymongo import MongoClient
from db import get_mongo_client
from auth import verify_token

router = APIRouter()

@router.post("/data_connectors", response_model=DataConnectorResponse)
async def add_data_connector(
    connector: DataConnectorCreate,
    client: MongoClient = Depends(get_mongo_client),
    user: dict = Depends(verify_token)
):
    user_id = user["user_id"]
    response = await create_data_connector(connector, user_id, client)
    if response is None:
        raise HTTPException(status_code=500, detail="Failed to create data connector")
    return response

@router.get("/data_connectors", response_model=List[DataConnectorResponse])
async def list_connectors(
    client: MongoClient = Depends(get_mongo_client),
    user: dict = Depends(verify_token)
):
    user_id = user["user_id"]
    return await get_data_connectors(user_id, client)
