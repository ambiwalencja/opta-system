from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from db import db_connect
from db_models import user_data, client_data, config
from routers import user_endpoints, client_endpoints, config_endpoints
from old_db import old_db_endpoints

# uvicorn main:app --reload
# http://127.0.0.1:8000/docs


if os.name == "nt":
    load_dotenv()

app = FastAPI(
    title="OPTA system",
    description="System dokumentacji i ewaluacji OPTA",
    version="0.1",
    # lifespan=lifespan
)

origins = [
    "http://localhost:3000",
    "*",  # Allow all origins for development purposes
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_endpoints.router)
app.include_router(client_endpoints.router)
app.include_router(config_endpoints.router)
app.include_router(old_db_endpoints.router)

@app.get("/")
def root():
    return "OPTA System"

db_connect.create_schema('client_data')
db_connect.create_schema('user_data')
db_connect.create_schema('config')

# create tables when starting program
db_connect.Base.metadata.create_all(db_connect.engine)
