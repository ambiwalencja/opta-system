from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from sqlalchemy.schema import CreateSchema

if os.name == "nt":
    load_dotenv()

DATABASE_URL = os.environ.get('DB_CONNECTION_STRING')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_schema(schema_name): # Create schemas if they don't exist
    with engine.connect() as connection:
        # Check if schema_a exists, if not, create it
        if not connection.dialect.has_schema(connection, schema_name):
            connection.execute(CreateSchema(schema_name))
            print(f"Schema {schema_name} created.")
        else:
            print(f"Schema {schema_name} already exists.")
        connection.commit() # Commit the schema creation
