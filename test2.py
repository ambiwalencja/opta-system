from db.db_connect import get_db
from sqlalchemy import text

db = next(get_db())

# Wrap the command in text() to execute it as raw SQL
db.execute(text('ALTER TABLE client_data.pacjenci ALTER COLUMN "Korzystanie_z_pomocy" TYPE jsonb USING "Korzystanie_z_pomocy"::jsonb'))
db.execute(text('ALTER TABLE client_data.pacjenci ALTER COLUMN "Problemy" TYPE jsonb USING "Problemy"::jsonb'))
db.execute(text('ALTER TABLE client_data.pacjenci ALTER COLUMN "Zaproponowane_wsparcie" TYPE jsonb USING "Zaproponowane_wsparcie"::jsonb'))

# Don't forget to commit and close manually if not using a function!
db.commit()
db.close()