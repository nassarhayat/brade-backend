import os
import json
import asyncpg
from typing import Optional, Any
from agents.configs.tools_dir.prices import get_stock_aggregates
from agents.configs.tools_dir.get_database_metadata import get_database_metadata, connect_to_supabase
from agents.configs.tools_dir.query_database import get_database_query
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

def get_stock_prices(stock_symbol: str):
    """
    gets stock data based on stock symbol
    
    Args:
      stock_symbol: e.g. AAPL, NVDA, MSFT, GOOG, AMZN, META, TSLA
    """
    global stock_data
    stock = get_stock_aggregates(stock_symbol)
    stock_data = stock
    return f"{stock_symbol} data fetched"

async def get_data_from_connected_databases(user_request: str):
    """
        Query SQL databases based on user request 
    """
    print("Received user request:", user_request)
    conn = await connect_to_supabase()
    try:
        metadata = await get_database_metadata(conn)
        sql_req = get_database_query(user_request, metadata)
        cleaned_query = sql_req.replace("```sql", "").replace("```", "").strip()

        # Log the query for debugging
        print("Executing query:", cleaned_query)
        
        results = await conn.fetch(cleaned_query)
        results_as_dicts = [dict(record) for record in results]
        return results_as_dicts
    except asyncpg.exceptions.UndefinedFunctionError as e:
        print("SQL Execution Error:", str(e))
        raise
    finally:
        await conn.close()

def get_historical_basis(user_question: str):
    """
        Exclusively focuses on historical data; does not address future expectations.
    """
    global trade_data
    base_dir = os.path.dirname(__file__)
    file_path = os.path.join(base_dir, '../../data/historical_basis_data.json')
    with open(file_path) as file:
        trade_data = json.load(file)
    
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": f"You are a helpful assistant that filters and transforms this data based on user question: {trade_data[:20]}. Only return with json array without extra text. do not ask clarifying questions"},
            {"role": "user", "content": user_question }
        ],
        response_format={ "type": "json_object" }
    )
    
    content = completion.choices[0].message.content
    try:
        result = json.loads(content)
        print("result-his", result)
        if isinstance(result, dict) and "trades" in result:
            trades_array = result["trades"] if isinstance(result["trades"], list) else [result["trades"]]
        elif isinstance(result, dict):
            trades_array = [result]
        else:
            trades_array = result
    except json.JSONDecodeError:
        print("Error: The model's response is not valid JSON.")
        trades_array = content 
    
    print("COMPLETION", trades_array)
    return trades_array

def get_client_trades(user_question: str, client_name: Optional[str] = None):
    """
        For questions about past, present, or future trades on a trader's clients.
        do not generate tool_response_store 
    """
    print(user_question, client_name, "USER+CLIENT")
    base_dir = os.path.dirname(__file__)
    file_path = os.path.join(base_dir, '../../data/fx_swaps.json')
    with open(file_path) as file:
        trade_data = json.load(file)
    
    # tool_response_store["get_client_trades"].append(trade_data[:20])
    return trade_data[:20]

def get_predicted_flows(tool_response_store: Any = None):
    """
        For questions about future market trends or predictions and questions involving net risk across tenors.
        do not generate tool_response_store 
    """
    data = [
        { "name": "1W", "DV01-negative": -30, "DV01-positive": 20 },
        { "name": "1M", "DV01-negative": -40, "DV01-positive": 30 },
        { "name": "3M", "DV01-negative": -10, "DV01-positive": 50 },
        { "name": "6M", "DV01-negative": -50, "DV01-positive": 60 },
        { "name": "9M", "DV01-negative": -15, "DV01-positive": 15 },
        { "name": "12M", "DV01-negative": -45, "DV01-positive": 45 }
    ]
    
    # tool_response_store["get_predicted_flows"].append(data)

    return data