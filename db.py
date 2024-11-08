from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from typing import Generator
# from supabase import create_client, Client

mongodb_pw = "bnABLnuHBF4twxy"
uri = f"mongodb+srv://nassarhayat:{mongodb_pw}@cluster0.tshuf.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

client = MongoClient(uri, server_api=ServerApi('1'))
database = client["brade_dev"]
collection = database["notebooks"]

def get_mongo_client() -> Generator[MongoClient, None, None]:
  try:
    yield client
  finally:
    pass

# SUPABASE_URL = os.getenv("SUPABASE_URL", "https://acejgpdnjeyknidwnkei.supabase.co")
# SUPABASE_KEY = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFjZWpncGRuamV5a25pZHdua2VpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjkwNTAwMTUsImV4cCI6MjA0NDYyNjAxNX0.XiIepSjoCQyjSzltvg3jSaAn1Po3tA6oNTOc9yoP89o")
# supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)