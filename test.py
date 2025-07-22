# import os
# from dotenv import load_dotenv
# from db import db_connect
# from db_models import user_data
# from db_models import client_data
# from db_models import config

# if os.name == "nt":
#     load_dotenv()

# # Create schemas
# db_connect.create_schema('client_data')
# db_connect.create_schema('user_data')
# db_connect.create_schema('config')

# # --- NEW DIAGNOSTIC ---
# print("\n--- Tables registered with Base.metadata before create_all ---")
# for table_name, table_obj in db_connect.Base.metadata.tables.items():
#     print(f"  {table_name} (Schema: {table_obj.schema})")
# print("----------------------------------------------------\n")
# # --- END NEW DIAGNOSTIC ---

# # Create all tables once
# db_connect.Base.metadata.create_all(db_connect.engine)
# print("All tables created successfully across all schemas.")

from datetime import datetime, timedelta, timezone
# print(datetime.now())
print(datetime.now(timezone.utc))