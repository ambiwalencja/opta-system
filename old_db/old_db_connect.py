from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
from fastapi import HTTPException

if os.name == "nt":
    load_dotenv()

engine = None
SessionLocal = None

def initialize_old_db():
    global engine, SessionLocal

    old_db_enabled = os.getenv("OLD_DB_MODE", "false").lower() == "true"
    if not old_db_enabled:
        print("Old DB mode is disabled. Skipping MySQL connection.")
        return

    OLD_DATABASE_URL = os.environ.get('OLD_DB_CONNECTION_STRING')
    print(f"Attempting to connect with URL: {OLD_DATABASE_URL}")

    try:
        engine = create_engine(OLD_DATABASE_URL)
        with engine.connect() as conn:
            print("Successfully connected to MySQL database!")
        SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    except Exception as e:
        print(f"Connection error: {str(e)}")


def get_db():
    if not SessionLocal:
        raise HTTPException(
            status_code=503,
            detail="Old DB connection is not available. Check if OLD_DB_MODE is enabled."
        )
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()