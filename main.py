from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from db import db_connect
from db_models import user_data, client_data, config

'''
TODO: status: sprawdzić jeszcze raz ostanią odpowiedź czata, część już rzeczy, które wskazał, zrobiłam
nadal nie wiem skąd ten błąd
raise exc.NoReferencedTableError(
sqlalchemy.exc.NoReferencedTableError: Foreign key associated with column 'wizyty_indywidualne.ID_pacjenta' could not find table 'pacjenci' with which to generate a foreign key to target column 'ID_pacjenta'
'''

# uvicorn main:app --reload
# http://127.0.0.1:8000/docs

# https://elarkk.github.io/blog/multi-schema-sqlalchemy # przykład tworzenia bazy ze schemami

# print('dupa')
# print(os.name)
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

# app.include_router(test_endpoints.router)
# app.include_router(users_endpoints.router)

@app.get("/")
def root():
    return "OPTA System"

db_connect.create_schema('client_data')
db_connect.create_schema('user_data')
db_connect.create_schema('config')

# create tables when starting program
print(id(db_connect.Base))
db_connect.Base.metadata.create_all(db_connect.engine)

# client_data.ClientDataBase.metadata.create_all(db_connect.engine)
# user_data.UserDataBase.metadata.create_all(db_connect.engine)
# config.ConfigBase.metadata.create_all(db_connect.engine)