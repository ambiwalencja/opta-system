import pandas as pd
from old_db.import_old_db import engine


with engine.connect() as connection:
    df = pd.read_sql_table("pacjenci", connection)

print("Successfully loaded data from MySQL! ⚙️")
print(df.head())