from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from sqlalchemy.schema import CreateSchema

# print('dupa db connect')
if os.name == "nt":
    load_dotenv()

DATABASE_URL = os.environ.get('DB_CONNECTION_STRING')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()
print(id(Base))

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


# def rebase(cls): # decorator for handling cross schema relationships
#         for name, attr in cls.__dict__.items():
#             if isinstance(attr, ForeignKey):
#                 # The ForeignKey string itself (e.g., 'UserData.user.ID_uzytkownika') handles the schema
#                 pass
#             if isinstance(attr, relationship):
#                 # For relationships, ensure the foreign side knows its schema
#                 # This logic helps if the relationship argument wasn't fully qualified (e.g., just "User" instead of "UserData.User")
#                 # and the related class's __table__ doesn't yet have its schema set from its Base
#                 # (though with the MetaData(schema=...) approach, it usually will)
#                 # The key is that the Base class for the related model already carries the schema info.
#                 pass
#         return cls