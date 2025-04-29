from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.environ.get('DB_CONNECTION_STRING')

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = declarative_base()
# https://elarkk.github.io/blog/multi-schema-sqlalchemy TODO: zmienić żeby były trzy bazowe zmienne po jednej na każdą schemę

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()