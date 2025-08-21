from sqlalchemy import create_engine
import os
from dotenv import load_dotenv


if os.name == "nt":
    load_dotenv()

# --- Connect to the TEMPORARY MySQL database ---
# The format is "mysql+pymysql://user:password@host/database_name"
OLD_DATABASE_URL = os.environ.get('OLD_DB_CONNECTION_STRING')
engine = create_engine(OLD_DATABASE_URL)
