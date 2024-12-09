import os
from pydantic import BaseModel
from models.session_context import SessionContext
from openai import OpenAI
from dotenv import load_dotenv
from agents.swarm.types import Result
from models.block import BlockType
from typing import Dict, List, Any
from services.document_service import get_documents

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

class BlockTypeResponse(BaseModel):
    recommended: BlockType
    rationale: str
    alternatives: List[BlockType]

def determine_block_type_llm(
    data: List[Dict[str, Any]], 
    user_request: str
) -> Dict[str, Any]:
    """
    Uses an LLM to determine the most suitable BlockType based on data and user request.
    Returns the recommended BlockType and rationale.
    """
    # If data is in spreadsheet format, return spreadsheet type
    if isinstance(data, dict):
        if 'cells' in data:
            return BlockType.spreadsheet
        if 'datasets' in data:
            # Check if it's a line chart or bar chart based on the user request
            if 'line' in user_request.lower():
                return BlockType.line_chart
            elif 'bar' in user_request.lower():
                return BlockType.bar_chart
            # Default to line chart if not specified
            return BlockType.line_chart

    # Convert dictionary to list if needed
    if isinstance(data, dict):
        data = list(data.values())

    data_preview = data[:3] 

    column_types = {}
    if data:
        first_row = data[0]
        if isinstance(first_row, dict):
            column_types = {key: type(value).__name__ for key, value in first_row.items()}
        elif isinstance(first_row, list):
            column_types = {f"column_{i}": type(value).__name__ for i, value in enumerate(first_row)}

    # Create LLM prompt
    prompt = f"""
    You are a data visualization assistant. Your job is to analyze data and determine the most suitable visualization type.

    Data preview (first 3 rows): {data_preview}
    Column types: {column_types}

    User request: "{user_request}"

    Based on this information, recommend the most appropriate visualization type
    """
    
    # Call OpenAI API
    response = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": "You are an expert in data visualization."},
            {"role": "user", "content": prompt},
        ],
        response_format=BlockTypeResponse,
    )

    # Parse response
    response_content = response.choices[0].message.parsed
    # print("LLM Response:", response_content)
    return response_content.recommended

async def data_transformer(
    user_request: str, 
    session_context: SessionContext = None,
) -> Result:
    print("Starting data_transformer with context documents:", session_context.context_document_ids)
    
    context_docs = {}
    
    try:
        if session_context.context_document_ids:
            context_docs = await get_documents(session_context.context_document_ids)
            # print("Retrieved context docs:", context_docs)
    except Exception as e:
        print(f"Error fetching context documents: {str(e)}")
        return Result(value=[], blockType="table", error="Error fetching documents")

    prev_step_output = session_context.get_last_step_output().value
    
    # Limit the data preview to reduce token count
    data_preview = prev_step_output[:3] if isinstance(prev_step_output, list) else list(prev_step_output.items())[:3]
    
    context_docs_preview = {}
    for doc_id, doc in context_docs.items():
        if isinstance(doc, dict):
            preview_data = {k: str(v)[:100] for k, v in doc.items()}
            context_docs_preview[doc_id] = preview_data
        else:
            context_docs_preview[doc_id] = {'preview': str(doc)[:200] + '...'}

    completion = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": """You are a code generator that ONLY returns Python code that creates output_data.
                Your entire response must be valid Python code.
                
                Available variables:
                - input_data: the data to transform (list of dictionaries or dictionary)
                - context_docs: the reference documents
                
                Required output formats by blockType:
                - table: output_data should be a list of dictionaries with consistent keys
                - spreadsheet: output_data must follow this exact pattern:
                    output_data = {
                        'cells': [
                            [{'value': col1}, {'value': col2}, ...],  # headers
                        ]
                    }
                    # Then add data rows using list comprehension:
                    output_data['cells'].extend(
                        [{'value': str(row['col1'])}, {'value': str(row['col2'])}, ...]
                        for row in input_data
                    )
                - line-chart/bar-chart: output_data must be exactly:
                    {
                        'labels': ['label1', 'label2', ...],
                        'datasets': [{'label': 'dataset1', 'data': [value1, value2, ...]}]
                    }
                
                DO NOT:
                - Import external libraries
                - Create or write files
                - Use print or display functions
                - Include any explanations
                
                ONLY return the Python code that creates output_data variable.
                """
            },
            {
                "role": "user",
                "content": f"Write code to transform this data: {data_preview} based on request: {user_request}"
            },
        ]
    )

    transformation_script = completion.choices[0].message.content.strip()
    # print("Transformation script:", transformation_script)
    
    try:
        # Provide context documents to the transformation script
        local_vars = {
            'input_data': prev_step_output,
            'context_docs': context_docs
        }
        exec(transformation_script, {}, local_vars)
        transformed_data = local_vars.get('output_data')
        
        if transformed_data is None:
            print("Warning: Transformation didn't produce output_data")
            return Result(value=prev_step_output, blockType="table", error="Transformation didn't produce output")
            
        print("Transformed data:", transformed_data)
        
        blockType = determine_block_type_llm(transformed_data, user_request)
        return Result(value=transformed_data, blockType=blockType)
        
    except Exception as e:
        print(f"Error executing transformation script: {str(e)}")
        print("Failed script:", transformation_script)
        return Result(
            value=prev_step_output, 
            blockType="table", 
            error=f"Transformation error: {str(e)}"
        )