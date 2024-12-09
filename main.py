import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import notebooks, data_connectors, documents, threads, documents_index
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

if os.getenv("TESTING") != "true":
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(notebooks.router)
app.include_router(data_connectors.router)
app.include_router(documents.router)
app.include_router(threads.router)
app.include_router(documents_index.router)