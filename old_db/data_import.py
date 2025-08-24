import pandas as pd
# from old_db.old_db_connect import engine
from sqlalchemy.orm import Session


def import_table_to_dataframe(table_name: str, db: Session):
    try:
        df = pd.read_sql_table(table_name, db.connection())
        print("Successfully loaded data from MySQL! ⚙️")
        # print(df.head())
        return df
    except Exception as e:
        print(f"Error loading data from MySQL: {e}")
        return None

 
