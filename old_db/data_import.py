import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from fastapi import HTTPException
from datetime import datetime
import ast
from io import BytesIO
from typing import Union

from schemas.pacjent_schemas import PacjentImport
from schemas.spot_grup_schemas import SpotkanieGrupoweCreate
from schemas.wizyta_schemas import WizytaIndywidualnaCreate, WizytaIndywidualnaImport
from schemas.user_schemas import UserCreate
from schemas.grupa_schemas import GrupaCreate, UczestnikGrupyCreate

from utils.pacjent_functions import import_pacjent
from utils.wizyta_functions import create_wizyta, import_wizyta
from utils.grupa_functions import create_grupa, create_uczestnik_grupy
from utils.spot_grup_functions import create_spotkanie_grupowe

from old_db.field_mappings import NAZWA_GRUPY_MAP, GRUPY_TABLE_MAP



def import_table_to_dataframe(table_name: str, db: Session, schema: str = None) -> pd.DataFrame:
    try:
        df = pd.read_sql_table(table_name, db.connection(), schema=schema)
        print("Successfully loaded data from database:")
        print(df.head())
        return df
    except Exception as e:
        print(f"Error loading data from database: {e}")
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

def reset_pacjent_sequence(db: Session) -> None:
    """Resets the PostgreSQL auto-increment sequence to MAX(ID_pacjenta) + 1."""
    # setval ("sequence_name", next_value, true/false) true means the next call to nextval() will return next_value + 1
    sql_command = text("""
        SELECT setval(
            pg_get_serial_sequence('client_data.pacjenci', 'ID_pacjenta'),
            (SELECT MAX("ID_pacjenta") FROM client_data.pacjenci), 
            true
        );
    """)
    
    try:
        db.execute(sql_command)
        db.commit()
        print("Successfully reset pacjenci ID sequence.")
    except Exception as e:
        db.rollback()
        print(f"Error resetting pacjenci ID sequence: {e}")

def import_pacjenci_to_new_db(df: pd.DataFrame, db: Session):
    # df = df.head(5) # for testing, limit
    # with open('test10.csv', 'w', newline='', encoding='utf-8') as f:
    #     df.to_csv(f, index=False)

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
            # Convert row to dict and create PacjentImport object
            pacjent_data = row.to_dict()
            
            # Convert date strings to date objects
            for date_field in ['Data_zgloszenia', 'Data_zakonczenia', 'Data_ostatniej_wizyty']:
                date_value = pacjent_data.get(date_field)
                if pd.isna(date_value): # NaN, NaT
                    pacjent_data[date_field] = None
                    continue

                try:
                    pacjent_data[date_field] = date_value.date() # we use this method because the object is already a Timestamp, not a string
                except AttributeError as e: # This catches if the object is *not* a Timestamp and *not* a datetime
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid date object type in row {index} for field {date_field}: {str(e)}"
                    )
            
            # Convert empty strings to None
            for key, value in pacjent_data.items():
                if isinstance(value, (list, tuple, dict, pd.Series)):
                    continue # Skip the missing value check for collections
                if isinstance(value, str):
                    if value.strip() == '':
                        pacjent_data[key] = None
                elif pd.isna(value): # NaN, NaT # we can't give a collection as an argument here, because it then returns a collection of bools, not a single bool
                    pacjent_data[key] = None
            
            # Create Pydantic model
            try:
                pacjent = PacjentImport(**pacjent_data)
                # print(f'Created PacjentImport model for row {index}: {pacjent}')
            except Exception as e:
                raise HTTPException(
                    status_code=422,
                    detail=f"Invalid data in row {index}: {str(e)}"
                )
            
            # Use the import_pacjent function directly
            imported_patient = import_pacjent(db, pacjent) #, id_uzytkownika=1
            
            success_count += 1
            # print(f"Successfully imported patient {pacjent.imie} {pacjent.nazwisko}")

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

    if results["success_count"] > 0:
        reset_pacjent_sequence(db) # resetting the sequence after bulk import to enable normal inserts
    
    return results

def reset_wizyta_sequence(db: Session) -> None:
    """Resets the PostgreSQL auto-increment sequence to MAX(ID_wizyty) + 1."""
    sql_command = text("""
        SELECT setval(
            pg_get_serial_sequence('client_data.wizyty_indywidualne', 'ID_wizyty'), 
            (SELECT MAX("ID_wizyty") FROM client_data.wizyty_indywidualne), 
            true
        );
    """)
    try:
        db.execute(sql_command)
        db.commit()
        print("Successfully reset wizyty ID sequence.")
    except Exception as e:
        db.rollback()
        print(f"Error resetting wizyty ID sequence: {e}")

def get_correct_pacjent_id(db: Session, current_pacjent_id: int):
    """
    Get the correct pacjent ID for wizyta import, accounting for duplicates.
    current_pacjent_id: The ID of the current pacjent which is/can be a duplicate
    """
    from db_models.client_data import pacjent_duplicates

    duplicate_record = db.query(pacjent_duplicates).filter(
        pacjent_duplicates.c.ID_zduplikowanego_pacjenta == current_pacjent_id
    ).first()
    
    if duplicate_record:
        # If it's a duplicate, use the original ID
        return duplicate_record.ID_pacjenta

    return current_pacjent_id

def import_wizyty_ind_to_new_db(df: pd.DataFrame, db: Session):
    # df = df.head(100) # for testing, limit
    
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
            # Convert row to dict and create ImportWizyta object
            wizyta_data = row.to_dict()
            
            # Convert date strings to date objects
            for date_field in ['Data_wizyty']:
                date_value = wizyta_data.get(date_field)
                if pd.isna(date_value): # NaN, NaT
                    wizyta_data[date_field] = None
                    continue

                try:
                    wizyta_data[date_field] = date_value.date() # we use this method because the object is already a Timestamp, not a string
                except AttributeError as e: # This catches if the object is *not* a Timestamp and *not* a datetime
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid date object type in row {index} for field {date_field}: {str(e)}"
                    )
            
            # Convert empty strings to None
            for key, value in wizyta_data.items():
                if isinstance(value, (list, tuple, dict, pd.Series)):
                    continue # Skip the missing value check for collections
                if isinstance(value, str):
                    if value.strip() == '':
                        wizyta_data[key] = None
                elif pd.isna(value): # NaN, NaT # we can't give a collection as an argument here, because it then returns a collection of bools, not a single bool
                    wizyta_data[key] = None
            
            # Create Pydantic model
            try:
                # wizyta_data['ID_pacjenta'] = get_correct_pacjent_id(db, wizyta_data['ID_pacjenta']) # not all duplicates are actually duplicates, must be handled manually
                wizyta = WizytaIndywidualnaImport(**wizyta_data)
            except Exception as e:
                raise HTTPException(
                    status_code=422,
                    detail=f"Invalid data in row {index}: {str(e)}"
                )
            
            created_wizyta = import_wizyta(db, wizyta)
            
            success_count += 1
            # print(f"Successfully imported wizyta {wizyta.data_wizyty} {wizyta.typ_wizyty}")

        except HTTPException as he:
            error_count += 1
            errors.append(str(he.detail))
            print(f"HTTP Error at row {index}: {he.detail}")
            continue
        except Exception as e:
            error_count += 1
            error_msg = f"Error importing wizyta at row {index}: {str(e)}"
            errors.append(error_msg)
            print(error_msg)
            db.rollback() # ???
            continue

    results = {
        "success_count": success_count,
        "error_count": error_count,
        "errors": errors
    }

    if results["success_count"] > 0:
        reset_wizyta_sequence(db) # resetting the sequence after bulk import to enable normal inserts
    
    return results

def import_grupy_from_dict_to_new_db(db: Session):
    for nr, attributes in GRUPY_TABLE_MAP.items():
        nazwa_grupy_value, data_rozp_value, typ_grupy_value = attributes
        input_data = {
            "Nazwa_grupy": nazwa_grupy_value,
            "Data_rozpoczecia": data_rozp_value,
            "Typ_grupy": typ_grupy_value
        }
        try:
            new_grupa = GrupaCreate(**input_data)
        except Exception as e:
                raise HTTPException(
                    status_code=422,
                    detail=f"Invalid data for number {nr}: {str(e)}"
                )
        try:
            create_grupa(db, new_grupa, id_uzytkownika=1)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error creating grupa for number {nr}: {str(e)}"
            )
    
    return True

def reset_uczestnik_grupy_sequence(db: Session) -> None:
    """Resets the PostgreSQL auto-increment sequence to MAX(ID_uczestnika_grupy) + 1."""
    sql_command = text("""
        SELECT setval(
            pg_get_serial_sequence('client_data.uczestnicy_grupy', 'ID_uczestnika_grupy'),
            (SELECT MAX("ID_uczestnika_grupy") FROM client_data.uczestnicy_grupy),
            true
        );
    """)
    try:
        db.execute(sql_command)
        db.commit()
        print("Successfully reset uczestnik_grupy ID sequence.")
    except Exception as e:
        db.rollback()
        print(f"Error resetting uczestnik_grupy ID sequence: {e}")

def import_uczestnicy_grupy_to_new_db(df: pd.DataFrame, db: Session):
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
            uczestnik_grupy_data = row.to_dict()
            
            # Convert empty strings to None
            for key, value in uczestnik_grupy_data.items():
                if isinstance(value, (list, tuple, dict, pd.Series)):
                    continue # Skip the missing value check for collections
                if isinstance(value, str):
                    if value.strip() == '':
                        uczestnik_grupy_data[key] = None
                elif pd.isna(value): # NaN, NaT # we can't give a collection as an argument here, because it then returns a collection of bools, not a single bool
                    uczestnik_grupy_data[key] = None
            
            # Create Pydantic model
            try:
                uczestnik_grupy = UczestnikGrupyCreate(**uczestnik_grupy_data)
            except Exception as e:
                raise HTTPException(
                    status_code=422,
                    detail=f"Invalid data in row {index}: {str(e)}"
                )
            
            created_uczestnik_grupy = create_uczestnik_grupy(db, uczestnik_grupy)
            
            success_count += 1

        except HTTPException as he:
            error_count += 1
            errors.append(str(he.detail))
            print(f"HTTP Error at row {index}: {he.detail}")
            continue
        except Exception as e:
            error_count += 1
            error_msg = f"Error importing uczestnik grupy at row {index}: {str(e)}"
            errors.append(error_msg)
            print(error_msg)
            db.rollback() # ???
            continue

    results = {
        "success_count": success_count,
        "error_count": error_count,
        "errors": errors
    }
    
    if results["success_count"] > 0:
        reset_uczestnik_grupy_sequence(db)
    
    return results


def import_spotkania_grupowe_to_new_db(df: pd.DataFrame, db: Session):
    # df = df.head(40)
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
            spotkanie_data = row.to_dict()
            
            for date_field in ['Data_spotkania']:
                date_value = spotkanie_data.get(date_field)
                if pd.isna(date_value):
                    spotkanie_data[date_field] = None
                    continue

                try:
                    spotkanie_data[date_field] = date_value.date() 
                except AttributeError as e:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid date object type in row {index} for field {date_field}: {str(e)}"
                    )
            
            for key, value in spotkanie_data.items():
                if isinstance(value, (list, tuple, dict, pd.Series)):
                    continue
                if isinstance(value, str):
                    if value.strip() == '':
                        spotkanie_data[key] = None
                elif pd.isna(value):
                    spotkanie_data[key] = None

            try:
                spotkanie = SpotkanieGrupoweCreate(**spotkanie_data)
            except Exception as e:
                raise HTTPException(
                    status_code=422,
                    detail=f"Invalid data in row {index}: {str(e)}"
                )

            created_spotkanie = create_spotkanie_grupowe(db, spotkanie, 1)

            success_count += 1
            # print(f"Successfully imported spotkanie {spotkanie.data_spotkania} {spotkanie.id_grupy}")
        except HTTPException as he:
            error_count += 1
            errors.append(str(he.detail))
            print(f"HTTP Error at row {index}: {he.detail}")
            continue
        except Exception as e:
            error_count += 1
            error_msg = f"Error importing spotkanie at row {index}: {str(e)}"
            errors.append(error_msg)
            print(error_msg)
            continue
    
    results = {
        "success_count": success_count,
        "error_count": error_count,
        "errors": errors
    }
    return results
