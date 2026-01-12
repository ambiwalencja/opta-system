from fastapi import HTTPException, status
from datetime import datetime
from sqlalchemy import Column, func, distinct, Date, Boolean, Integer, desc
from sqlalchemy.orm import aliased, Query
from sqlalchemy.orm.session import Session
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from typing import Optional, Dict, Any, List

from auth.hashing import Hash
from db_models.client_data import Pacjent, WizytaIndywidualna #, Grupa
from schemas.pacjent_schemas import (
    BaseModel, PacjentCreateBasic, PacjentCreateForm, # PacjentDisplay, 
    PacjentUpdate, PacjentImport
)
from utils.validation import validate_choice, validate_choice_fields
from utils.safe_mappings import SORTABLE_FIELDS, FILTERING_FIELDS, SEARCHABLE_FIELDS


def get_pacjent_by_id(db: Session, id_pacjenta: int):
    pacjent = db.query(Pacjent).filter(Pacjent.ID_pacjenta == id_pacjenta).first()
    if not pacjent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Pacjent with ID {id_pacjenta} not found")
    return pacjent

def check_pacjent_duplicates(db: Session, pacjent_data: PacjentCreateBasic):
    # Check for duplicates - phone
    if pacjent_data.telefon:
        duplicate = db.query(Pacjent).filter(Pacjent.Telefon == pacjent_data.telefon).first()
        if duplicate:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "message": f'Client with phone number {pacjent_data.telefon} already exists',
                    "duplicate_id": duplicate.ID_pacjenta
                }
            )
    
    # Check for duplicates - email
    if pacjent_data.email:
        duplicate = db.query(Pacjent).filter(Pacjent.Email == pacjent_data.email).first()
        if duplicate:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "message": f'Client with email {pacjent_data.email} already exists',
                    "duplicate_id": duplicate.ID_pacjenta
                }
            )
    
    # Check for duplicates - name and address
    duplicate = db.query(Pacjent).filter(
        Pacjent.Imie == pacjent_data.imie,
        Pacjent.Nazwisko == pacjent_data.nazwisko,
        Pacjent.Dzielnica == pacjent_data.dzielnica,
        # Pacjent.Ulica == pacjent_data.ulica, # na ten moment kasujemy dokładny adres z warunku
        # Pacjent.Nr_domu == pacjent_data.nr_domu
    ).first()
    
    if duplicate:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": f'Client with name {pacjent_data.imie} {pacjent_data.nazwisko} and the same address already exists',
                "duplicate_id": duplicate.ID_pacjenta
            }
        )
    return None 

def check_pacjent_duplicates_for_import(db: Session, pacjent_data: PacjentCreateBasic):
    """
    Check for duplicates and return original pacjent info instead of raising exception.
    Returns:
        None if no duplicate found
        List[original_pacjent_id, duplicate_field, duplicate_value] if duplicate found
    """
    # Check for duplicates - phone
    if pacjent_data.telefon:
        original_pacjent = db.query(Pacjent).filter(Pacjent.Telefon == pacjent_data.telefon).first()
        if original_pacjent:
            return [original_pacjent.ID_pacjenta, "Telefon", pacjent_data.telefon]
    
    # Check for duplicates - email
    if pacjent_data.email:
        original_pacjent = db.query(Pacjent).filter(Pacjent.Email == pacjent_data.email).first()
        if original_pacjent:
            return [original_pacjent.ID_pacjenta, "Email", pacjent_data.email]

    # Check for duplicates - name and address
    original_pacjent = db.query(Pacjent).filter(
        Pacjent.Imie == pacjent_data.imie,
        Pacjent.Nazwisko == pacjent_data.nazwisko,
        Pacjent.Dzielnica == pacjent_data.dzielnica,
    ).first()
    if original_pacjent:
        return [original_pacjent.ID_pacjenta, "Imie,Nazwisko,Dzielnica", f'{pacjent_data.imie} {pacjent_data.nazwisko} ({pacjent_data.dzielnica})']

    return None

def record_pacjent_duplicate(db: Session, original_id: int, duplicate_id: int, duplicate_field: str, duplicate_value: str = None) -> None:
    """
    Record a duplicate relationship in the pacjent_duplicates table.
    
    Args:
        original_id: The ID_pacjenta that was kept (the original)
        duplicate_id: The ID_pacjenta that is a duplicate
        duplicate_field: Which field(s) caused the duplicate (e.g., "Telefon", "Email")
        duplicate_value: Optional - the actual value that was duplicated
    """
    from sqlalchemy import insert
    from db_models.client_data import pacjent_duplicates
    
    try:
        stmt = insert(pacjent_duplicates).values(
            ID_pacjenta=original_id,
            ID_zduplikowanego_pacjenta=duplicate_id,
            Duplicated_field=duplicate_field,
            Duplicated_value=duplicate_value
        )
        db.execute(stmt)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error recording duplicate relationship: {e}")
    
def create_pacjent_basic(db: Session, pacjent_data: PacjentCreateBasic, id_uzytkownika: int):
    # 1. Check for duplicates
    check_pacjent_duplicates(db, pacjent_data)
    # 2. Dynamic validation of all choice fields (here - only dzielnica)
    validate_choice_fields(db, pacjent_data)
    # 3. Convert to dict with DB column names
    data_dict = pacjent_data.model_dump(by_alias = True, exclude_unset = True)

    # 4. Add backend-generated fields
    data_dict["Created"] = datetime.now()
    data_dict["Last_modified"] = datetime.now()
    data_dict["ID_uzytkownika"] = id_uzytkownika

    # 6. Create SQLAlchemy object
    new_pacjent = Pacjent(**data_dict)
    # 7. actually add to DB
    db.add(new_pacjent)
    db.commit()
    db.refresh(new_pacjent)
    return new_pacjent

def import_pacjent(db: Session, pacjent_data: PacjentImport): # , id_uzytkownika: int
    # 1. Check for duplicates
    duplicate_result = check_pacjent_duplicates_for_import(db, pacjent_data)
    # 2. Dynamic validation of all choice fields
    validate_choice_fields(db, pacjent_data)
    # 3. Convert to dict with DB column names
    data_dict = pacjent_data.model_dump(by_alias = True, exclude_unset = True)

    # 4. Add backend-generated fields
    data_dict["Created"] = datetime.now()
    data_dict["Last_modified"] = datetime.now()
    # data_dict["ID_uzytkownika"] = id_uzytkownika

    # 5. Conditional cleanup - optional
    if not data_dict.get("Niebieska_karta"):
        data_dict["Niebieska_karta_inicjator"] = None
        data_dict["Grupa_robocza"] = None
        data_dict["Grupa_robocza_sklad"] = None
        data_dict["Plan_pomocy"] = None
        data_dict["Plan_pomocy_opis"] = None
        data_dict["Narzedzia_prawne"] = None
        data_dict["Zawiadomienie"] = None
    
    # 6. Create SQLAlchemy object
    # print(f'Importing pacjent with data: /n {data_dict}') #test
    new_pacjent = Pacjent(**data_dict)
    # print(f'Created Pacjent object: /n {new_pacjent}') #test
    # 7. actually add to DB
    db.add(new_pacjent) 
    db.commit() 
    db.refresh(new_pacjent)

    # 8. If duplicate found, record it
    if duplicate_result:
        original_id, duplicate_field, duplicate_value = duplicate_result
        record_pacjent_duplicate(db, original_id, new_pacjent.ID_pacjenta, duplicate_field, duplicate_value)
        print(f"Duplicate recorded: {new_pacjent.Imie} {new_pacjent.Nazwisko} is duplicate of ID {original_id}")
    
    return new_pacjent

def core_update_pacjent(db: Session, id_pacjenta: int, pacjent_data: BaseModel): # BaseModel, żeby mógł przyjmować PacjentCreateForm i PacjentUpdate
    # 1. Check that pacjent exists and find it
    existing_pacjent = get_pacjent_by_id(db, id_pacjenta)
    
    # 2. Dynamic validation of all choice fields
    validate_choice_fields(db, pacjent_data)
    
    # 3. Convert to dict with DB column names
    data_dict = pacjent_data.model_dump(by_alias = True, exclude_unset = True)
    
    # 4. Add backend-generated fields
    data_dict["Last_modified"] = datetime.now()
    # data_dict["ID_uzytkownika"] = id_uzytkownika # można się zastanowić, czy tutaj zmieniać rejestrującego

    # 5. Conditional cleanup - optional
    if "Niebieska_karta" in data_dict and not data_dict.get("Niebieska_karta"):
        data_dict["Niebieska_karta_inicjator"] = None
        data_dict["Grupa_robocza"] = None
        data_dict["Grupa_robocza_sklad"] = None
        data_dict["Plan_pomocy"] = None
        data_dict["Plan_pomocy_opis"] = None
        data_dict["Narzedzia_prawne"] = None
        data_dict["Zawiadomienie"] = None

    # 6. Update fields in existing object
    for key, value in data_dict.items():
        setattr(existing_pacjent, key, value)
    
    # 7. Commit changes to DB
    db.commit()
    db.refresh(existing_pacjent)
    return existing_pacjent

def update_pacjent(db: Session, id_pacjenta: int, pacjent_data: PacjentUpdate):
    return core_update_pacjent(db, id_pacjenta, pacjent_data)

def create_pacjent_form(db: Session, id_pacjenta: int, pacjent_data: PacjentCreateForm):
    return core_update_pacjent(db, id_pacjenta, pacjent_data)

def get_recent_pacjenci(db: Session, id_uzytkownika: int, limit: int = 10):
    # Create an alias for WizytaIndywidualna to use in the subquery
    WizytaAlias = aliased(WizytaIndywidualna)
    LatestWizyta = aliased(WizytaIndywidualna)

    # Subquery to get the top 10 patient IDs and their latest visit dates
    latest_visits_subquery = (
        db.query(
            WizytaAlias.ID_pacjenta,
            # func.max(WizytaAlias.Data_wizyty).label('latest_visit_date'),
            func.max(WizytaAlias.ID_wizyty).label('latest_visit_id')
        )
        .filter(WizytaAlias.ID_uzytkownika == id_uzytkownika)
        .group_by(WizytaAlias.ID_pacjenta)
        .order_by(func.max(WizytaAlias.Data_wizyty).desc())
        .limit(limit)
        .subquery()
    )
    
    # patient_ids = db.query(latest_visits_subquery.c.ID_pacjenta).all()
    # print([id[0] for id in patient_ids])

    # Main query to fetch patient details and the specific latest visit details
    pacjent_list = (
        db.query(
             # Pacjent, # Selecting the full Pacjent object is often simpler here
            Pacjent.ID_pacjenta,
            Pacjent.Imie, 
            Pacjent.Nazwisko,
            Pacjent.Data_zgloszenia,
            Pacjent.Email,
            Pacjent.Telefon,
            Pacjent.Dzielnica,
            Pacjent.Ulica,
            Pacjent.Nr_domu,
            Pacjent.Nr_mieszkania,
            Pacjent.Status_pacjenta,
            LatestWizyta.ID_wizyty,
            LatestWizyta.Typ_wizyty, # Use the alias for selection
            LatestWizyta.Data_wizyty          # Use the alias for selection
        )
        # JOIN 1: Filter Pacjent to the top 10 IDs (Explicit ON required)
        .join(
            latest_visits_subquery, 
            Pacjent.ID_pacjenta == latest_visits_subquery.c.ID_pacjenta
        )
        # JOIN 2: Use the ALIAS (LatestWizyta) as the target, and provide the full compound ON clause.
        .join(
            LatestWizyta, # Use the ALIAS (the model) as the target
            (LatestWizyta.ID_pacjenta == Pacjent.ID_pacjenta) & # <-- MUST re-introduce the FK link
            (LatestWizyta.ID_wizyty == latest_visits_subquery.c.latest_visit_id)
            # (LatestWizyta.Data_wizyty == latest_visits_subquery.c.latest_visit_date)
        )
        .filter(LatestWizyta.ID_uzytkownika == id_uzytkownika)
        .order_by(LatestWizyta.Data_wizyty.desc())
        .all()
    )

    # # Debug: Print results
    # print(len(pacjent_list), "patients retrieved.")
    # print("\nSelected patients with their most recent visits:")
    # for pacjent, wizyta in pacjent_list:
    #     print(f"Patient {pacjent.ID_pacjenta}: {pacjent.Imie} {pacjent.Nazwisko}, Last visit: {wizyta.Data}")

    return pacjent_list

def get_recently_created_pacjenci(db: Session, limit: int = 10):
    pacjent_list = (
        db.query(Pacjent)
        .order_by(Pacjent.Created.desc())
        .limit(limit)
        .all()
    )
    return pacjent_list

def delete_pacjent(db: Session, id_pacjenta: int):
    pacjent = get_pacjent_by_id(db, id_pacjenta)
    db.delete(pacjent)
    db.commit()
    return {"detail": f"Pacjent with ID {id_pacjenta} deleted successfully"}

def search_pacjenci(query: Query, search_term: str = None):
    if search_term:
        search_like = f"%{search_term}%"
        query = query.filter(
            (Pacjent.Imie.ilike(search_like)) | 
            (Pacjent.Nazwisko.ilike(search_like)) |
            (Pacjent.Email.ilike(search_like)) |
            (Pacjent.Telefon.ilike(search_like))
        )
    return query

def filter_pacjenci(query: Query, filters: List[str] = None):
    # Parse filters from list of "field:value" strings
    filter_params = {}
    if filters:
        for f in filters:
            if ':' in f:
                field, value = f.split(':', 1)
                filter_params[field.strip()] = value.strip()

    # FILTERING
    for param_name, value_str in filter_params.items():
        column_to_filter: Optional[Column] = FILTERING_FIELDS.get(param_name)
        
        if column_to_filter:
            if isinstance(column_to_filter.type, Boolean):
                if value_str.lower() in ('true', '1'):
                    value = True
                elif value_str.lower() in ('false', '0'):
                    value = False
                else:
                    continue 
            elif isinstance(column_to_filter.type, Date):
                # Check if it's a date range (format: "2023-01-01,2023-12-31")
                if ',' in value_str:
                    try:
                        date_parts = value_str.split(',')
                        start_date = datetime.strptime(date_parts[0].strip(), "%Y-%m-%d").date()
                        end_date = datetime.strptime(date_parts[1].strip(), "%Y-%m-%d").date()
                        query = query.filter(column_to_filter.between(start_date, end_date))
                        continue
                    except (ValueError, IndexError):
                        continue
                else:
                    try:
                        value = datetime.strptime(value_str, "%Y-%m-%d").date()
                        query = query.filter(column_to_filter >= value)
                        continue
                    except ValueError:
                        continue
            elif isinstance(column_to_filter.type, Integer):
                try:
                    value = int(value_str)
                except ValueError:
                    continue
            else:
                value = value_str
                
            query = query.filter(column_to_filter == value)
    return query

def sort_pacjenci(query: Query, sort_by: str, sort_direction: str):
    sort_column: Optional[Column] = SORTABLE_FIELDS.get(sort_by)
    if not sort_column:
        sort_column = Pacjent.ID_pacjenta

    if sort_direction == 'desc':
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(sort_column)
    return query

def get_all_pacjenci(
        db: Session, 
        sort_by: str, 
        sort_direction: str,
        search_term: str = None,
        filters: List[str] = None
    ) -> Page[Pacjent]:
    
    query = db.query(Pacjent)
    query = search_pacjenci(query, search_term)
    query = filter_pacjenci(query, filters)
    query = sort_pacjenci(query, sort_by, sort_direction)

    return paginate(query)