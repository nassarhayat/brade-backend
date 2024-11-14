import os
import json 
import asyncio
from typing import Optional
from swarm import Swarm, Agent
from openai import OpenAI
from .prices import get_stock_aggregates
from .trades import get_fx_swap_trades
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

openai_client = OpenAI(api_key=api_key)
client = Swarm(client=openai_client)

stock_data = None
trade_data = None
transformed_data = []

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

def get_historical_basis(user_question: str):
    """
    gets data on historical basis to answer questions like
    What has 3m USDJPY basis done in the last 3 months and last year?
    Always say you have the data and respond with message that answers question 
    with range from -2.8 to 5.2. don't say you don't have the da
    """
    global trade_data
    base_dir = os.path.dirname(__file__)
    file_path = os.path.join(base_dir, '../data/historical_basis_data.json')
    with open(file_path) as file:
        trade_data = json.load(file)
    
    completion = openai_client.chat.completions.create(
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

def get_client_trades(user_question: str, client: Optional[str] = None):
    """
    gets data on client trades to answer questions
    only use client filter if user asks for specific client trades
    always return data as a array of objects without nested objects.
    
    summary and table with client, expected volume, side, and PV01 
    (e.g. Pfizher, 200m, buy, 5k)
    """
    global trade_data
    base_dir = os.path.dirname(__file__)
    file_path = os.path.join(base_dir, '../data/fx_swaps.json')
    with open(file_path) as file:
        trade_data = json.load(file)
    # print("TRADE", trade_data)
    if not client:
        completion = openai_client.chat.completions.create(
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
    search_term_lower = client.lower()
    matched_trades = [
        trade for trade in trade_data if search_term_lower in trade.get("client_name", "").lower()
    ]
    print("Matched trades:", matched_trades)
    return matched_trades[:20]

def get_predicted_flows():
    """
    gets predicted flows for a client. it charts tenors and risk. highlight where
    there is a net difference for each tenor with numbers for each returned in summary
    when asked for next week then respond with answer with all tenors in mind.
    
    """
    data = [
        { 'name': '1W', 'DV01-negative': -30, 'DV01-positive': 20 },
        { 'name': '1M', 'DV01-negative': -40, 'DV01-positive': 30 },
        { 'name': '3M', 'DV01-negative': -10, 'DV01-positive': 50 },
        { 'name': '6M', 'DV01-negative': -50, 'DV01-positive': 60 },
        { 'name': '9M', 'DV01-negative': -15, 'DV01-positive': 15 },
        { 'name': '12M', 'DV01-negative': -45, 'DV01-positive': 45 },
    ]

    return data

def transfer_to_data_fetcher():
    return data_fetcher

def transfer_to_data_transformer():
    global stock_data
    print("Transformed time series data:", stock_data)
    global transformed_data
    for entry in stock_data["time_series_data"]:
        timestamp = datetime.fromtimestamp(entry['t'] / 1000).strftime('%Y-%m-%d %H:%M:%S')
        transformed_entry = {
            "timestamp": timestamp,
            "open": entry['o'],
            "close": entry['c']
        }
        transformed_data.append(transformed_entry)
    
    print("TRANS", transformed_data)
    return data_transformer

def transfer_to_data_loader():
    return data_loader

data_fetcher = Agent(
    name="Data fetcher",
    instructions="""
        You are a helpful agent that answers questions on 
        - client trades - e.g. "Let’s drill down, which clients are likely to be trading the bulk of 3m USDJPY swaps with me in the next week?"
        - historical basis
        - predicted flows
        use get_historical_basis when asked about past flows and make predictions on that data.
        respond with summary one line answers if you use tools to get data. 
        don't ask clarifying questions.
    """,
    functions=[get_client_trades, get_predicted_flows, get_historical_basis, transfer_to_data_transformer],
)

data_transformer = Agent(
    name="Data Transformer",
    instructions="say I transformed fetched data and talk to data loader",
    # functions=[transfer_to_data_loader]
)

data_loader = Agent(
    name="Data Loader",
    instructions="say I have loaded data into a format to be viewed then fetch data"
)

async def run_swarm(message: str):
    response = client.run(
        agent=data_fetcher,
        messages=[{"role": "user", "content": message}],
        stream=True
    )
    
    for message in response:
        print("Messagfe", message)
        json_chunk = ""
        if message.get("delim"):
            pass
        elif message.get("response"):
            # print("respose", message)
            messages = message['response'].messages
            for mes in messages:
                if mes['role'] == 'tool':
                    print("mes", mes)
                    if mes['tool_name'] == 'transfer_to_data_transformer':
                        json_chunk = json.dumps({
                            "role": "tool",
                            "toolType": "chart",
                            "content": transformed_data
                        })
                    elif mes['tool_name'] == 'get_predicted_flows':
                        print("mes original content:", mes['content'])
                        if isinstance(mes['content'], str):
                            try:
                                mes['content'] = json.loads(mes['content'].replace("'", '"'))
                                print("Parsed content as JSON:", mes['content'])
                            except json.JSONDecodeError:
                                try:
                                    mes['content'] = ast.literal_eval(mes['content'])
                                    print("Parsed content using ast.literal_eval:", mes['content'])
                                except (ValueError, SyntaxError) as e:
                                    print("Error parsing mes['content'] as a Python literal:", e)
                                    mes['content'] = []

                        json_chunk = json.dumps({
                            "role": "tool",
                            "toolType": "stacked-chart",
                            "content": mes['content']
                        })
                        print("Final json_chunk:", json_chunk)
                    elif mes['tool_name'] == 'get_historical_basis':
                        print("mes original content:", mes['content'])
                        if isinstance(mes['content'], str):
                            try:
                                mes['content'] = json.loads(mes['content'].replace("'", '"'))
                                print("Parsed content as JSON:", mes['content'])
                            except json.JSONDecodeError:
                                try:
                                    mes['content'] = ast.literal_eval(mes['content'])
                                    print("Parsed content using ast.literal_eval:", mes['content'])
                                except (ValueError, SyntaxError) as e:
                                    print("Error parsing mes['content'] as a Python literal:", e)
                                    mes['content'] = []

                        json_chunk = json.dumps({
                            "role": "tool",
                            "toolType": "line-chart",
                            "content": mes['content']
                        })
                        print("Final json_chunk:", json_chunk)
                    elif mes['tool_name'] == 'get_client_trades':
                        print("mes-get-trades original content:", mes['content'])
                        # Check if mes['content'] is a string that needs to be converted
                        if isinstance(mes['content'], str):
                            try:
                                # Try parsing as JSON
                                mes['content'] = json.loads(mes['content'].replace("'", '"'))
                                print("Parsed mes['content'] as JSON:", mes['content'])
                            except json.JSONDecodeError:
                                try:
                                    # Fallback to parsing as a Python literal if JSON parsing fails
                                    mes['content'] = ast.literal_eval(mes['content'])
                                    print("Parsed mes['content'] using ast.literal_eval:", mes['content'])
                                except (ValueError, SyntaxError) as e:
                                    print("Error parsing mes['content'] as a Python literal:", e)
                                    mes['content'] = []  # Fallback to an empty list if parsing fails

                        # Check if mes['content'] is now a list after parsing
                        if isinstance(mes['content'], list):
                            json_chunk = json.dumps({
                                "role": "tool",
                                "toolType": "table",
                                "content": mes['content']  # Pass the Python list directly
                            })
                        else:
                            print("Error: mes['content'] is not a list even after parsing")
                            json_chunk = json.dumps({
                                "role": "tool",
                                "toolType": "table",
                                "content": []  # Fallback to an empty array if needed
                            })
                    else:
                        print("mes-content", mes['content'])
                        json_chunk = json.dumps({
                            "role": "tool",
                            "content": mes['content']
                        })
        else:
            json_chunk = json.dumps({
                "content": message["content"]
            })
        yield json_chunk
        await asyncio.sleep(0) 
    

    # json_messages = [
    #     {"role": message["role"], "content": message["content"]}
    #     for message in response.messages
    # ]

    # json_output = json.dumps({"messages": json_messages}, indent=2)
    # return json_output
    

# response = client.run(
#     agent=data_fetcher,
#     messages=[{
#         "role": "user",
#         "content": "what is the price of apple today?"
#     }]
# )

# for message in response.messages:
#     print(message["role"], " ", message["content"])

# json_messages = []
# for message in response.messages:
#     json_messages.append({
#         "role": message["role"],
#         "content": message["content"]
#     })

# # Convert the list of messages to a JSON string
# json_output = json.dumps({"messages": json_messages}, indent=4)

# print(json_output)