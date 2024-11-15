from pydantic import BaseModel
from typing import List, Optional, Any
from fastapi import HTTPException, Query, APIRouter, Depends
from pymongo.mongo_client import MongoClient
from fastapi.responses import StreamingResponse
from services.agents import run_swarm
from services.notebooks import get_notebooks_service, create_notebook_service, \
  get_notebook_service, add_thread_item_service, add_block_to_notebook_service, \
  get_blocks_for_notebook_service
from db import get_mongo_client
from auth import verify_token
from schemas.notebook import Notebook, NotebooksResponse, NotebookCreateRequest, NotebookResponse
from schemas.thread import ThreadItemCreateRequest
from schemas.block import Block, BlockCreateRequest, BlockAddResponse

router = APIRouter(dependencies=[Depends(verify_token)])

@router.post("/notebooks", response_model=NotebookResponse)
async def create_notebook(request: NotebookCreateRequest, client: MongoClient = Depends(get_mongo_client)):
  # print(request, "request")
  notebook = create_notebook_service(request.userRequest, client)
  print("N", notebook)
  if not notebook:
    raise HTTPException(status_code=500, detail=f"Failed to create notebook")
  return notebook
  
@router.get("/notebooks", response_model=List[NotebooksResponse])
async def get_notebooks(
  filter_by: Optional[str] = Query(None, title="Filter notebooks by type"),
  client: MongoClient = Depends(get_mongo_client),
):
  notebooks = get_notebooks_service(filter_by, client)
  if not notebooks:
      raise HTTPException(status_code=500, detail="No notebooks found")
  return notebooks

@router.get("/notebooks/{notebook_id}", response_model=NotebookResponse)
async def get_notebook(notebook_id: str, client: MongoClient = Depends(get_mongo_client)):
  notebook = get_notebook_service(notebook_id, client)
  # print(notebook, "NOTEBOOK")
  if not notebook:
    raise HTTPException(status_code=404, detail="Notebook not found")
  return notebook

@router.post("/notebooks/{notebook_id}/thread-items", response_model=NotebookResponse)
async def add_thread_item(
  notebook_id: str,
  thread_item_data: ThreadItemCreateRequest,
  client: MongoClient = Depends(get_mongo_client),
  # user: Any = Depends(verify_token)
):
  response_generator = add_thread_item_service(notebook_id, thread_item_data, "user.id", client)
  return StreamingResponse(response_generator, media_type="text/event-stream")

@router.patch("/notebooks/{notebook_id}/blocks", response_model=BlockAddResponse)
async def add_block_to_notebook_dashboard(
  notebook_id: str,
  block_data: BlockCreateRequest,
  client: MongoClient = Depends(get_mongo_client),
  # user: Any = Depends(verify_token)
):
  response_generator = add_block_to_notebook_service(
    notebook_id,
    block_data.id, 
    "user.id",
    client
  )
  return response_generator

@router.get("/notebooks/{notebook_id}/blocks", response_model=List[Block])
async def get_blocks_for_notebook(notebook_id: str, client: MongoClient = Depends(get_mongo_client)):
  blocks = get_blocks_for_notebook_service(notebook_id, client)
  if not blocks:
    return []
  return blocks