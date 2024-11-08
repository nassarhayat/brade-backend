import json 
import asyncio
from swarm import Swarm, Agent
from .market_data import get_stock_data
from datetime import datetime
# from dotenv import load_dotenv
# import os

# load_dotenv()
# api_key = os.getenv("OPENAI_API_KEY")
# print("API", api_key)
client = Swarm()

# data = {
#     "stock": [
#         { "id": "12456", "name": "APPL", "price": 450.50 },
#         { "id": "12456", "name": "TSLA", "price": 350.66 },
#     ],
#     "transactions": [
#         { "id": "12456", "name": "james", "amount": 2450.50 },
#         { "id": "12456", "name": "caleb", "amount": 999.99 },
#     ]
# }

stock_data = None
transformed_data = []

def get_stock_prices(stock_symbol: str):
    """
    gets stock data based on stock symbol
    
    Args:
      stock_symbol: e.g. AAPL, NVDA, MSFT, GOOG, AMZN, META, TSLA
    """
    global stock_data
    stock = get_stock_data(stock_symbol)
    stock_data = stock
    return f"{stock_symbol} data fetched"

def transfer_to_data_fetcher():
    return data_fetcher

def transfer_to_data_transformer():
    global stock_data
    print("Transformed time series data:", stock_data)
    global transformed_data
    for entry in stock_data["time_series_data"]:
        timestamp = datetime.utcfromtimestamp(entry['t'] / 1000).strftime('%Y-%m-%d %H:%M:%S')
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
    instructions="You are a helpful agent. that can fetch stock data and once fetched, transfer to transformer",
    functions=[get_stock_prices, transfer_to_data_transformer],
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