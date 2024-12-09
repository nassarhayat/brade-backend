import asyncio
import sys
from pathlib import Path

# Add the project root to Python path
root_dir = Path(__file__).parent.parent.parent.parent
sys.path.append(str(root_dir))

from data_transformer import data_transformer
from models.session_context import SessionContext
from agents.swarm.types import Result

async def main():
    # Test 1: Spreadsheet format
    spreadsheet_data = [
        {
            "id": "14",
            "Country/Currency": "Bahamas Dollar",
            "currency": "BSD",
            "value": 1.132608,
            "date": "17/12/2021"
        },
        # ... other data ...
    ]
    
    session_context = SessionContext()
    session_context.set_context_document_ids(["4KjhdEkEWRrzf43DAyzLjauiyyf9"])
    result = Result(value=spreadsheet_data, blockType="spreadsheet")
    session_context.add_step({
        "tool_name": "previous_step",
        "output": result
    })
    
    try:
        result = await data_transformer(
            user_request="convert this to spreadsheet format",
            session_context=session_context
        )
        print("\nSpreadsheet Test:")
        print("Block Type:", result.blockType)
        print("Data Structure:", type(result.value))
        if isinstance(result.value, dict):
            if 'cells' in result.value:
                print("✓ Correct spreadsheet format")
                print("Number of rows:", len(result.value['cells']))
                print("First row:", result.value['cells'][0] if result.value['cells'] else "Empty")
            else:
                print("✗ Missing 'cells' key in spreadsheet format")
        else:
            print("✗ Wrong data structure for spreadsheet")
            print("Actual data:", result.value)
    except Exception as e:
        print(f"Error testing spreadsheet transformer: {str(e)}")

    # Test 2: Line Chart
    line_chart_data = [
        {"month": "Jan", "sales": 30, "costs": 20},
        {"month": "Feb", "sales": 45, "costs": 25},
        {"month": "Mar", "sales": 60, "costs": 30}
    ]
    
    session_context = SessionContext()
    session_context.set_context_document_ids(["line_chart_doc_id"])
    result = Result(value=line_chart_data, blockType="table")
    session_context.add_step({
        "tool_name": "previous_step",
        "output": result
    })
    
    try:
        result = await data_transformer(
            user_request="show this as a line chart comparing sales and costs over months",
            session_context=session_context
        )
        print("\nLine Chart Test:")
        print("Block Type:", result.blockType)
        print("Data Structure:", type(result.value))
        if isinstance(result.value, dict):
            if all(key in result.value for key in ['labels', 'datasets']):
                print("✓ Correct line chart format")
                print("Labels:", result.value['labels'])
                print("Datasets:", len(result.value['datasets']), "series")
            else:
                print("✗ Missing required keys in line chart format")
                print("Found keys:", result.value.keys())
    except Exception as e:
        print(f"Error testing line chart transformer: {str(e)}")

    # Test 3: Bar Chart
    bar_chart_data = [
        {"category": "Electronics", "revenue": 1200},
        {"category": "Clothing", "revenue": 800},
        {"category": "Books", "revenue": 400},
        {"category": "Food", "revenue": 600}
    ]
    
    session_context = SessionContext()
    session_context.set_context_document_ids(["bar_chart_doc_id"])
    result = Result(value=bar_chart_data, blockType="table")
    session_context.add_step({
        "tool_name": "previous_step",
        "output": result
    })
    
    try:
        result = await data_transformer(
            user_request="create a bar chart showing revenue by category",
            session_context=session_context
        )
        print("\nBar Chart Test:")
        print("Block Type:", result.blockType)
        print("Data Structure:", type(result.value))
        if isinstance(result.value, dict):
            if all(key in result.value for key in ['labels', 'datasets']):
                print("✓ Correct bar chart format")
                print("Number of categories:", len(result.value['labels']))
                print("Data points:", len(result.value['datasets'][0]['data']))
            else:
                print("✗ Missing required keys in bar chart format")
                print("Found keys:", result.value.keys())
    except Exception as e:
        print(f"Error testing bar chart transformer: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())