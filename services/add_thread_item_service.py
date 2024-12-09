import json
import asyncio
from typing import AsyncGenerator
from pymongo.mongo_client import MongoClient
from schemas.thread import ThreadItemCreateRequest, ThreadItemUserType
from models.thread import ThreadItemModel, ThreadItemUserType
from models.block import BlockType
from models.session_context import SessionContext
from repositories.threads import add_thread_item_repo
from agents.configs.agents import general_agent
from agents.swarm import Swarm
from bson.objectid import ObjectId
from services.document_service import update_document
from datetime import datetime

def format_block_data(data: any, block_type: str) -> dict:
    """
    Formats data based on block type for document storage
    """
    current_time = datetime.utcnow()
    
    # Base metadata
    metadata = {
        'type': block_type,
        'created': current_time.isoformat()
    }
    
    if block_type == "spreadsheet":
        # Data should already be in correct format with 'cells' key
        if isinstance(data, dict) and 'cells' in data:
            return {
                'cells': data['cells'],
                'metadata': metadata
            }
        # Convert list of dicts to cells format if needed
        formatted_cells = []
        if isinstance(data, list):
            if data and isinstance(data[0], dict):
                # Create headers from first row keys
                headers = list(data[0].keys())
                formatted_cells.append([{'value': str(h)} for h in headers])
                # Add data rows
                for row in data:
                    formatted_cells.append([{'value': str(row.get(h, ''))} for h in headers])
            else:
                # Handle list of non-dict items
                formatted_cells = [[{'value': str(item)} for item in data]]
        else:
            # Handle single value
            formatted_cells = [[{'value': str(data)}]]
            
        return {
            'cells': formatted_cells,
            'metadata': metadata
        }
        
    elif block_type in ["line-chart", "bar-chart", "chart"]:
        if isinstance(data, dict) and 'datasets' in data and 'labels' in data:
            return {
                'content': data,  # Keep chart data as is
                'metadata': metadata
            }
        # Convert list of dicts to chart format if needed
        if isinstance(data, list) and data and isinstance(data[0], dict):
            # Assume first numeric field is the data field
            numeric_field = next((k for k, v in data[0].items() if isinstance(v, (int, float))), None)
            label_field = next((k for k in data[0].keys() if k != numeric_field), None)
            
            if numeric_field and label_field:
                return {
                    'content': {
                        'labels': [str(item[label_field]) for item in data],
                        'datasets': [{
                            'label': numeric_field,
                            'data': [item[numeric_field] for item in data]
                        }]
                    },
                    'metadata': metadata
                }
                
    # Default table format
    return {
        'content': data,
        'metadata': metadata
    }

async def add_thread_item_service(
    thread_id: str,
    thread_item_data: ThreadItemCreateRequest,
    user_id: str,
    client: MongoClient,
) -> AsyncGenerator[str, None]:
    """
    Adds a thread item to a thread and interacts with an agent to process responses.
    Yields processed responses from the agent.
    """
    # Initialize thread items and context
    thread_items = list(client.brade_dev.thread_items.find(
        {"thread_id": ObjectId(thread_id)}
    ).sort("created", -1).limit(20))
    
    messages = [
        {
            "role": "assistant" if item["userType"] == "assistant" else "user",
            "content": item["content"]
        }
        for item in thread_items
    ]
    messages.append({"role": "user", "content": thread_item_data.content})
    
    # Add user message to thread
    user_thread_item = ThreadItemModel(
        content=thread_item_data.content,
        userType=ThreadItemUserType.user,
        userId=user_id,
        thread_id=thread_id,
        context_document_ids=thread_item_data.contextDocumentIds
    )
    add_thread_item_repo(thread_id, user_thread_item, client)

    # Run agent
    session_context = SessionContext()
    session_context.set_context_document_ids(thread_item_data.contextDocumentIds)
    swarm_client = Swarm()
    
    agent_response = await swarm_client.run(
        agent=general_agent,
        messages=messages,
        session_context=session_context,
        stream=True,
    )

    response_content = ""
    block_document_id = None

    async for message in agent_response:
        if message.get("response"):
            # Handle tool responses
            for tool_message in message["response"].messages:
                if tool_message.get("role") == "tool":
                    try:
                        last_step_output = session_context.get_last_step_output()
                        if not last_step_output or not hasattr(last_step_output, 'value'):
                            continue

                        block_type = last_step_output.blockType if hasattr(last_step_output, 'blockType') else "table"
                        doc_data = format_block_data(last_step_output.value, block_type)

                        doc_id = None
                        if thread_item_data.contextDocumentIds and len(thread_item_data.contextDocumentIds) > 0:
                            doc_id = str(thread_item_data.contextDocumentIds[0])

                        result = await update_document(doc_id, doc_data)
                        
                        if isinstance(result, dict) and result.get('documentId'):
                            block_document_id = str(result['documentId'])
                            
                        yield json.dumps({
                            "role": "tool",
                            "blockDocumentId": block_document_id
                        })
                    except Exception as e:
                        print(f"Error processing tool response: {str(e)}")
                        import traceback
                        print(traceback.format_exc())
                        
        elif "content" in message:
            content = message.get("content", "")
            if content is not None:
                response_content += content
                yield json.dumps({
                    "content": content,
                    "blockDocumentId": block_document_id
                })

    # Save final assistant message with all document IDs
    if response_content:
        assistant_thread_item = ThreadItemModel(
            content=response_content,
            userType=ThreadItemUserType.assistant,
            steps=session_context.steps,
            thread_id=thread_id,
            block_document_id=block_document_id
        )
        add_thread_item_repo(thread_id, assistant_thread_item, client)