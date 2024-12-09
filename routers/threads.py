from fastapi import HTTPException, Query, APIRouter, Depends
from pymongo.mongo_client import MongoClient
from fastapi.responses import StreamingResponse
from services.thread_service import (
    create_thread_service,
    get_threads_service,
    get_thread_service,
    # add_thread_item_service
)
from db import get_mongo_client
from services.add_thread_item_service import add_thread_item_service
# from auth import verify_token
from schemas.thread import ThreadResponse, ThreadItemCreateRequest, ThreadsResponse, ThreadCreateRequest

router = APIRouter()

@router.post("/threads", response_model=ThreadResponse)
async def create_thread(
        thread_request: ThreadCreateRequest,
        client: MongoClient = Depends(get_mongo_client) 
):
    print("Thread request:", thread_request)
    thread = create_thread_service(thread_request.userRequest, client)
    if not thread:
        raise HTTPException(status_code=500, detail="Failed to create thread")
    return thread
  
@router.get("/threads", response_model=ThreadsResponse)
async def get_threads(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100, alias="page_size"),
    client: MongoClient = Depends(get_mongo_client)
):
    threads = get_threads_service(page, page_size, client)
    # print("Threads data from service:", threads)  # Debug print

    if not threads:
        raise HTTPException(status_code=500, detail="Failed to fetch threads")
    return threads

@router.get("/threads/{thread_id}", response_model=ThreadResponse)
async def get_thread(
    thread_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    client: MongoClient = Depends(get_mongo_client)
):
    # print("Getting thread:", thread_id)
    thread = get_thread_service(thread_id, page, page_size, client)
    print("Thread data from service:", thread)
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    return thread

@router.post("/threads/{thread_id}", response_model=ThreadResponse)
async def add_thread_item(
    thread_id: str,
    thread_item_data: ThreadItemCreateRequest,
    client: MongoClient = Depends(get_mongo_client),
):
    # print("Adding thread item:", thread_item_data)
    response_generator = add_thread_item_service(thread_id, thread_item_data, "user.id", client)
    # print("Response generator:", response_generator)
    return StreamingResponse(response_generator, media_type="text/event-stream")