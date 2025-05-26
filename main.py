from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from db import db_connect
from db_models import client_data, user_data, config


# uvicorn main:app --reload
# http://127.0.0.1:8000/docs

print('dupa')
print(os.name)
if os.name == "nt":
    load_dotenv()

app = FastAPI(
    title="Automations",
    description="Automations API",
    version="0.1",
    # lifespan=lifespan
)

origins = [
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.include_router(find_person_endpoints.router)
# # app.include_router(test_endpoints.router)
# app.include_router(users_endpoints.router)

@app.get("/")
def root():
    return "Automations API"

# create tables when starting program
client_data.ClientDataBase.metadata.create_all(db_connect.engine)
user_data.UserDataBase.metadata.create_all(db_connect.engine)
config.ConfigBase.metadata.create_all(db_connect.engine)