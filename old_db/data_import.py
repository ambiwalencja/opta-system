import pandas as pd
# from old_db.old_db_connect import engine
from sqlalchemy.orm import Session
from fastapi import HTTPException
from schemas.client_schemas import CreatePacjent
from utils.client_functions import create_pacjent
from datetime import datetime


def import_table_to_dataframe(table_name: str, db: Session):
    try:
        df = pd.read_sql_table(table_name, db.connection())
        print("Successfully loaded data from MySQL! ⚙️")
        print(df.head())
        return df
    except Exception as e:
        print(f"Error loading data from MySQL: {e}")
        return None

 

def import_pacjenci_to_new_db(df: pd.DataFrame, db: Session):
    if df is None or df.empty:
        raise HTTPException(
            status_code=400,
            detail="No data to import"
        )
    
    success_count = 0
    error_count = 0
    errors = []

    for index, row in df.iterrows():
        try:
            # Convert row to dict and create CreatePacjent object
            pacjent_data = row.to_dict()
            
            # Convert date strings to date objects
            for date_field in ['Data_zgloszenia', 'Data_zakonczenia', 'Data_ostatniej_wizyty']:
                if date_field in pacjent_data and pacjent_data[date_field]:
                    try:
                        pacjent_data[date_field] = datetime.strptime(
                            str(pacjent_data[date_field]), '%Y-%m-%d'
                        ).date()
                    except ValueError as e:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Invalid date format in row {index} for field {date_field}: {str(e)}"
                        )

            # Create Pydantic model
            try:
                pacjent = CreatePacjent(**pacjent_data)
            except Exception as e:
                raise HTTPException(
                    status_code=422,
                    detail=f"Invalid data in row {index}: {str(e)}"
                )
            
            # Use the create_pacjent function directly
            created_patient = create_pacjent(db, pacjent)
            
            success_count += 1
            print(f"Successfully imported patient {pacjent.imie} {pacjent.nazwisko}")

        except HTTPException as he:
            error_count += 1
            errors.append(str(he.detail))
            print(f"HTTP Error at row {index}: {he.detail}")
            continue
        except Exception as e:
            error_count += 1
            error_msg = f"Error importing patient at row {index}: {str(e)}"
            errors.append(error_msg)
            print(error_msg)
            continue

    results = {
        "success_count": success_count,
        "error_count": error_count,
        "errors": errors
    }
    
    return results