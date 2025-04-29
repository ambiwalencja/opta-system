from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from db.db_connect import engine
from db_models import grupa, pacjent, spotkanie_grupowe, uzytkownik, wizyta_indywidualna


# uvicorn main:app --reload
# http://127.0.0.1:8000/docs


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
grupa.Base.metadata.create_all(engine)
pacjent.Base.metadata.create_all(engine)
spotkanie_grupowe.Base.metadata.create_all(engine)
uzytkownik.Base.metadata.create_all(engine)
wizyta_indywidualna.Base.metadata.create_all(engine)
