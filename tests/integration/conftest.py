import pytest
from fastapi.testclient import TestClient
from main import app
from pymongo.mongo_client import MongoClient
import certifi
import os
import pymongo
from dotenv import load_dotenv
from db import get_mongo_client

load_dotenv()

@pytest.fixture(scope="session")
def mongo_client():
    # Use local MongoDB if available, otherwise use test Atlas instance
    try:
        client = MongoClient('mongodb://localhost:27017')
        # Test the connection
        client.admin.command('ping')
        print("Connected to local MongoDB")
    except pymongo.errors.ConnectionFailure:
        print("Falling back to Atlas MongoDB")
        mongodb_pw = os.getenv("MONGODB_PW")
        test_uri = f"mongodb+srv://nassarhayat:{mongodb_pw}@cluster0.tshuf.mongodb.net/brade_test"
        client = MongoClient(
            test_uri,
            tlsCAFile=certifi.where(),
            serverSelectionTimeoutMS=5000
        )
        # Test the connection
        client.admin.command('ping')
    
    # Override the database to use test database
    client.database = client.brade_test
    
    # Override the app's dependency
    app.dependency_overrides[get_mongo_client] = lambda: client
    
    yield client
    
    app.dependency_overrides.clear()
    client.close()

@pytest.fixture(scope="session")
def test_client():
    return TestClient(app)

@pytest.fixture(autouse=True)
def setup_teardown(mongo_client):
    # Clear test data before each test
    mongo_client.brade_test.threads.delete_many({})
    mongo_client.brade_test.thread_items.delete_many({})
    yield
 