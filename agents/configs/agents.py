from agents.configs.tools import get_data_from_connected_databases
from agents.configs.tools_dir.data_transformer import data_transformer
from agents.configs.tools_dir.get_data_from_json_files import get_data_from_json_files
# from agents.data.routines.prompts import STARTER_PROMPT
from agents.swarm import Agent


def transfer_to_general_agent():
    return general_agent

def transfer_to_data_visualiser():
    return data_visualiser

def transfer_to_data_loader():
    return data_loader

general_agent = Agent(
    name="General agent",
    instructions="""
        You are an intelligent financial assistant specializing in client trades, market data, and predictions.
    
        1. start by getting data based on user query 
            1. get_data_from_connected_databases - for data that doesn't sit in on of the json files
            2. get_data_from_json_files - for json files: fx_swaps.json or historical_basis_data.json
        
        2. then transform data using data_transformer 
        
        always do both steps
        
        don't ask clarifying questions.
    """,
    functions=[get_data_from_connected_databases, data_transformer, get_data_from_json_files],
)

data_visualiser = Agent(
    name="Data Transformer",
    instructions="always call data_transformer",
    functions=[data_transformer]
)

data_loader = Agent(
    name="Data Loader",
    instructions="say I have loaded data into a format to be viewed then fetch data"
)
