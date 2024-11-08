from pydantic import BaseModel
from typing import List, Optional
from fastapi import HTTPException, Query, APIRouter, Depends
from pymongo.mongo_client import MongoClient
from services.threads import create_thread_service, get_thread_service
from db import get_mongo_client
from schemas.thread import Thread, ThreadCreateRequest, ThreadResponse

router = APIRouter()

@router.post("/threads", response_model=ThreadResponse)
async def create_thread(
  request: ThreadCreateRequest,
  client: MongoClient = Depends(get_mongo_client)
):
  print(request, "request")
  thread = create_thread_service(request.userRequest, client)
  print("N", thread)
  if not thread:
    raise HTTPException(status_code=500, detail=f"Failed to create thread")
  return thread

@router.get("/threads/{thread_id}", response_model=ThreadResponse)
async def get_thread(thread_id: str, client: MongoClient = Depends(get_mongo_client)):
  thread = get_thread_service(thread_id, client)
  if not thread:
    raise HTTPException(status_code=404, detail="Thread not found")
  return thread

@router.post("/threads/{thread_id}", response_model=Thread)
async def update_thread(
  thread_id: str,
  thread_data: ThreadCreateRequest,
  client: MongoClient = Depends(get_mongo_client)
):
  print(thread_data, "thread_data")
  # thread = get_thread_service(thread_id, client)
  # if not thread:
  #   raise HTTPException(status_code=404, detail="Thread not found")
  # return thread