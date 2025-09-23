import pandas as pd
# from old_db.old_db_connect import engine
from sqlalchemy.orm import Session
from fastapi import HTTPException
from schemas.client_schemas import CreatePacjent
from utils.client_functions import create_pacjent
# from utils.user_functions import create_user
from datetime import datetime
import ast
from io import BytesIO
from typing import Union
from schemas.user_schemas import UserCreate

def import_table_to_dataframe(table_name: str, db: Session, schema: str = None) -> pd.DataFrame:
    try:
        df = pd.read_sql_table(table_name, db.connection(), schema=schema)
        print("Successfully loaded data from MySQL! ⚙️")
        print(df.head())
        return df
    except Exception as e:
        print(f"Error loading data from MySQL: {e}")
        return None

def import_users_from_csv_complex(file_path: str) -> list[UserCreate]:
    """Import users from CSV file and convert to UserBase objects.
    This is iterative and handles errors in more detail."""
    try:
        # Read CSV file
        df = pd.read_csv(file_path)
        
        # Validate required columns
        required_columns = {'full_name', 'username', 'password', 'role', 'specjalista'}
        missing_columns = required_columns - set(df.columns)
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")

        users = []
        for index, row in df.iterrows():
            try:
                # Convert string of specializations to list
                specjalista = [s.strip() for s in str(row['specjalista']).split(',')]
                
                # Create UserCreate object with validation
                user = UserCreate(
                    full_name=row['full_name'],
                    username=row['username'],
                    password=row['password'],  # Note: password should be hashed
                    role=row['role'],
                    status=row.get('status', 'active'),  # Default to active if not provided
                    specjalista=specjalista
                )
                users.append(user)
                
            except Exception as e:
                print(f"Error processing row {index}: {str(e)}")
                continue
                
        return users
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error reading CSV file: {str(e)}"
        )

def import_users_from_csv_simple(file_source: Union[str, BytesIO]) -> list[UserCreate]:
    """Import users from CSV file and convert to UserBase objects.
    This is vertorized and handles errors automatically."""
    df = pd.read_csv(
        file_source,
        sep=';',           # use semicolon as separator
        skiprows=1,        # skip the "Table 1" row
        encoding='utf-8'
        )
    
    # Vectorized operation on entire column
    # df['specjalista'] = df['specjalista'].str.split(',').str.strip()
    df['Specjalista'] = df['Specjalista'].apply(ast.literal_eval)

    # Convert entire DataFrame to list of dicts at once
    users_data = df.to_dict('records')
    
    # List comprehension for conversion
    return [UserCreate(**user_data) for user_data in users_data]

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
