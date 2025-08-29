from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker


if os.name == "nt":
    load_dotenv()

# --- Connect to the TEMPORARY MySQL database ---
# The format is "mysql+pymysql://user:password@host/database_name"
OLD_DATABASE_URL = os.environ.get('OLD_DB_CONNECTION_STRING')

# engine = create_engine(OLD_DATABASE_URL)
print(f"Attempting to connect with URL: {OLD_DATABASE_URL}")

try:
    engine = create_engine(OLD_DATABASE_URL)
    # Test the connection
    with engine.connect() as conn:
        print("Successfully connected to MySQL database!")
except Exception as e:
    print(f"Connection error: {str(e)}")


SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()