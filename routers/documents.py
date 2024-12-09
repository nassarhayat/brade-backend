import httpx
from fastapi import APIRouter, HTTPException
from schemas.documents import DocumentCreate, DocumentUpdate, DocumentResponse

router = APIRouter()
NODE_SERVER_URL = "http://localhost:3030"

async def forward_to_node(method: str, path: str, json: dict = None):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(
                method=method,
                url=f"{NODE_SERVER_URL}/{path}",
                json=json
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=e.response.status_code if hasattr(e, 'response') else 500,
                              detail=str(e))

@router.post("/documents", response_model=DocumentResponse)
async def create_document(document: DocumentCreate):
    return await forward_to_node("POST", "documents", document.model_dump())

@router.get("/documents/{doc_id}", response_model=DocumentResponse)
async def get_document(doc_id: str):
    return await forward_to_node("GET", f"documents/{doc_id}")

@router.post("/documents/{document_id}", response_model=DocumentResponse)
async def update_document(document_id: str, document_update: DocumentUpdate):
    return await forward_to_node(
        "POST", 
        f"documents/{document_id}", 
        document_update.model_dump(exclude_unset=True)
    )
