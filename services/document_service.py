import aiohttp
import json
from typing import Dict, Any, Optional, List
from aiohttp import WSMsgType

# Global variables for connection state
_session = None
_ws = None
REPO_URL = "ws://localhost:3030/api"

async def connect():
    """Establish WebSocket connection to the Automerge repo server"""
    global _session, _ws
    if not _session:
        _session = aiohttp.ClientSession()
        _ws = await _session.ws_connect(REPO_URL)

async def close():
    """Close the WebSocket connection"""
    global _session, _ws
    if _session:
        await _ws.close()
        await _session.close()
        _session = None
        _ws = None

async def _send_and_receive(message: Dict) -> Optional[Dict]:
    """Helper function to handle WebSocket communication"""
    try:
        await _ws.send_json(message)
        
        while True:
            msg = await _ws.receive()
            
            if msg.type == WSMsgType.TEXT:
                return json.loads(msg.data)
            elif msg.type == WSMsgType.CLOSED:
                print("WebSocket closed")
                return None
            elif msg.type == WSMsgType.ERROR:
                print("WebSocket error:", msg.data)
                return None
            
    except Exception as e:
        print(f"WebSocket error: {str(e)}")
        return None

async def get_document(doc_id: str) -> Optional[Dict[str, Any]]:
    """Fetch a document from the Automerge repo"""
    try:
        await connect()
        
        message = {
            "type": "get_document",
            "documentId": doc_id
        }
        
        response = await _send_and_receive(message)
        if response and response.get("type") == "document":
            return response.get("content")
        
        return None
        
    except Exception as e:
        print(f"Error getting document: {str(e)}")
        return None

async def get_documents(doc_ids: List[str]) -> Dict[str, Any]:
    """Fetch multiple documents from the Automerge repo"""
    results = {}
    try:
        await connect()  # Connect once for all documents
        
        for doc_id in doc_ids:
            doc = await get_document(doc_id)
            if doc:
                results[doc_id] = doc
                
    finally:
        await close()  # Ensure connection is closed
        
    return results

async def update_document(doc_id: str | None, content: Dict[str, Any]) -> Dict[str, Any] | bool:
    """Create or update a document in the Automerge repo"""
    try:
        await connect()
        
        if doc_id and not isinstance(doc_id, str):
            doc_id = str(doc_id)
            
        message = {
            "type": "update_document",
            "documentId": doc_id if doc_id else None,
            "content": content
        }
        
        response = await _send_and_receive(message)
        return response if response else False
        
    finally:
        await close() 