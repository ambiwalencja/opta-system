import sqlalchemy as sa
from sqlalchemy import create_engine, ForeignKey, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

def rebase(cls): # decorator for handling cross schema relationships
    for name, attr in cls.__dict__.items():
        if isinstance(attr, ForeignKey):
            # The ForeignKey string itself (e.g., 'UserData.user.ID_uzytkownika') handles the schema
            pass
        if isinstance(attr, relationship):
            # For relationships, ensure the foreign side knows its schema
            # This logic helps if the relationship argument wasn't fully qualified (e.g., just "User" instead of "UserData.User")
            # and the related class's __table__ doesn't yet have its schema set from its Base
            # (though with the MetaData(schema=...) approach, it usually will)
            # The key is that the Base class for the related model already carries the schema info.
            pass
    return cls

DATABASE_URL = os.environ.get('DB_CONNECTION_STRING')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# Base = declarative_base()

# https://elarkk.github.io/blog/multi-schema-sqlalchemy TODO: umieścić tables w schemas
# abstrakcyjne klasy są niepotrzebne
# foreign keys zrealizować według klasycznego rozwiązania sqlalchemy, bez dekoratorów
# jeden plik na schemę, nie na model

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()