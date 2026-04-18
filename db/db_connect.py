from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from sqlalchemy.schema import CreateSchema
from sqlalchemy.exc import ProgrammingError
import json

# if os.name == "nt":
#     load_dotenv()
load_dotenv()  # Load environment variables from .env file

DATABASE_URL = os.environ.get('DB_CONNECTION_STRING')

# A function to handle the JSON serialization
def json_serializer(obj):
    # This ensures that non-ASCII characters are not escaped
    return json.dumps(obj, ensure_ascii=False)

# A function to handle the JSON deserialization (optional but good practice)
def json_deserializer(obj):
    return json.loads(obj)

# Create the SQLAlchemy engine with the custom serializers
engine = create_engine(
    DATABASE_URL,
    json_serializer=json_serializer,
    json_deserializer=json_deserializer,
    connect_args={"connect_timeout": 15}
)

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
        try:
            # Check if schema exists, if not, create it
            if not connection.dialect.has_schema(connection, schema_name):
                connection.execute(CreateSchema(schema_name))
                print(f"Schema {schema_name} created.")
                connection.commit()
            else:
                print(f"Schema {schema_name} already exists.")
        except ProgrammingError as e:
            # Handle race condition where schema was created by another worker
            if "already exists" in str(e):
                print(f"Schema {schema_name} already exists.")
                connection.rollback()
            else:
                raise
