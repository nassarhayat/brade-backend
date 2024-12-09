import os
import json 

def get_data_from_json_files(user_query: str, json_file_name: str):
    """
        For questions about past, present, or future trades on a trader's clients.
        do not generate tool_response_store 
    """
    print(user_query, json_file_name, "USER+FILENAME")
    base_dir = os.path.dirname(__file__)
    file_path = os.path.join(base_dir, f"../../../data/{json_file_name}")
    with open(file_path) as file:
        json_data = json.load(file)
    
    return json_data