from fastapi import HTTPException, status
from datetime import datetime
from sqlalchemy import Column, func, distinct, Date, Boolean, Integer, desc, or_
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import aliased, Query
from sqlalchemy.orm.session import Session
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from typing import Optional, Dict, Any, List
import logging
import json

from auth.hashing import Hash
from db_models.client_data import Pacjent, WizytaIndywidualna #, Grupa
from schemas.pacjent_schemas import (
    BaseModel, PacjentCreateBasic, PacjentCreateForm, # PacjentDisplay, 
    PacjentUpdate, PacjentImport
)
from utils.validation import validate_choice, validate_choice_fields
from utils.safe_mappings import SORTABLE_FIELDS, FILTERING_FIELDS, SEARCHABLE_FIELDS

logger = logging.getLogger("opta_system_logger")


def get_pacjent_by_id(db: Session, id_pacjenta: int):
    try:
        pacjent = db.query(Pacjent).filter(Pacjent.ID_pacjenta == id_pacjenta).first()
        if not pacjent:
            logger.warning("Pacjent with ID %d not found", id_pacjenta)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Pacjent with ID {id_pacjenta} not found")
        logger.debug("Pacjent with ID %d retrieved successfully", id_pacjenta)
        return pacjent
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error retrieving pacjent with ID %d: %s", id_pacjenta, str(e), exc_info=True)
        raise

def check_pacjent_duplicates(db: Session, pacjent_data: PacjentCreateBasic):
    try:
        # Check for duplicates - phone
        if pacjent_data.telefon:
            duplicate = db.query(Pacjent).filter(Pacjent.Telefon == pacjent_data.telefon).first()
            if duplicate:
                logger.warning("Duplicate pacjent found by phone %s (ID: %d)", pacjent_data.telefon, duplicate.ID_pacjenta)
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
                logger.warning("Duplicate pacjent found by email %s (ID: %d)", pacjent_data.email, duplicate.ID_pacjenta)
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
            logger.warning("Duplicate pacjent found by name/address: %s %s (ID: %d)", pacjent_data.imie, pacjent_data.nazwisko, duplicate.ID_pacjenta)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "message": f'Client with name {pacjent_data.imie} {pacjent_data.nazwisko} and the same address already exists',
                    "duplicate_id": duplicate.ID_pacjenta
                }
            )
        logger.debug("No duplicates found for pacjent: %s %s", pacjent_data.imie, pacjent_data.nazwisko)
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error checking pacjent duplicates: %s", str(e), exc_info=True)
        raise 

def check_pacjent_duplicates_for_import(db: Session, pacjent_data: PacjentCreateBasic):
    """
    Check for duplicates and return original pacjent info instead of raising exception.
    Returns:
        None if no duplicate found
        List[original_pacjent_id, duplicate_field, duplicate_value] if duplicate found
    """
    try:
        # Check for duplicates - phone
        if pacjent_data.telefon:
            original_pacjent = db.query(Pacjent).filter(Pacjent.Telefon == pacjent_data.telefon).first()
            if original_pacjent:
                logger.debug("Import duplicate detected by phone %s (original ID: %d)", pacjent_data.telefon, original_pacjent.ID_pacjenta)
                return [original_pacjent.ID_pacjenta, "Telefon", pacjent_data.telefon]
        
        # Check for duplicates - email
        if pacjent_data.email:
            original_pacjent = db.query(Pacjent).filter(Pacjent.Email == pacjent_data.email).first()
            if original_pacjent:
                logger.debug("Import duplicate detected by email %s (original ID: %d)", pacjent_data.email, original_pacjent.ID_pacjenta)
                return [original_pacjent.ID_pacjenta, "Email", pacjent_data.email]

        # Check for duplicates - name and address
        original_pacjent = db.query(Pacjent).filter(
            Pacjent.Imie == pacjent_data.imie,
            Pacjent.Nazwisko == pacjent_data.nazwisko,
            Pacjent.Dzielnica == pacjent_data.dzielnica,
        ).first()
        if original_pacjent:
            logger.debug("Import duplicate detected by name/address: %s %s (original ID: %d)", pacjent_data.imie, pacjent_data.nazwisko, original_pacjent.ID_pacjenta)
            return [original_pacjent.ID_pacjenta, "Imie,Nazwisko,Dzielnica", f'{pacjent_data.imie} {pacjent_data.nazwisko} ({pacjent_data.dzielnica})']

        return None
    except Exception as e:
        logger.error("Error checking pacjent duplicates for import: %s", str(e), exc_info=True)
        raise

def record_pacjent_duplicate(db: Session, original_id: int, duplicate_id: int, duplicate_field: str, duplicate_value: str = None) -> None:
    """
    Record a duplicate relationship in the pacjent_duplicates table.
    
    Args:
        original_id: The ID_pacjenta that was kept (the original)
        duplicate_id: The ID_pacjenta that is a duplicate
        duplicate_field: Which field(s) caused the duplicate (e.g., "Telefon", "Email")
        duplicate_value: Optional - the actual value that was duplicated
    """
    try:
        from sqlalchemy import insert
        from db_models.client_data import pacjent_duplicates
        
        stmt = insert(pacjent_duplicates).values(
            ID_pacjenta=original_id,
            ID_zduplikowanego_pacjenta=duplicate_id,
            Duplicated_field=duplicate_field,
            Duplicated_value=duplicate_value
        )
        db.execute(stmt)
        db.commit()
        logger.info("Recorded duplicate relationship: original_id=%d, duplicate_id=%d, field=%s", original_id, duplicate_id, duplicate_field)
    except Exception as e:
        db.rollback()
        logger.error("Error recording duplicate relationship (original_id=%d, duplicate_id=%d): %s", original_id, duplicate_id, str(e), exc_info=True)
    
def create_pacjent_basic(db: Session, pacjent_data: PacjentCreateBasic, id_uzytkownika: int):
    try:
        logger.info("Creating new pacjent: %s %s", pacjent_data.imie, pacjent_data.nazwisko)
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
        logger.info("Pacjent created successfully with ID: %d", new_pacjent.ID_pacjenta)
        return new_pacjent
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error creating pacjent %s %s: %s", pacjent_data.imie, pacjent_data.nazwisko, str(e), exc_info=True)
        raise

def import_pacjent(db: Session, pacjent_data: PacjentImport): # , id_uzytkownika: int
    try:
        logger.info("Starting pacjent import: %s %s", pacjent_data.imie, pacjent_data.nazwisko)
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
        logger.info("Pacjent imported successfully with ID: %d", new_pacjent.ID_pacjenta)

        # 8. If duplicate found, record it
        if duplicate_result:
            original_id, duplicate_field, duplicate_value = duplicate_result
            record_pacjent_duplicate(db, original_id, new_pacjent.ID_pacjenta, duplicate_field, duplicate_value)
            print(f"Duplicate recorded: {new_pacjent.Imie} {new_pacjent.Nazwisko} is duplicate of ID {original_id}")
        
        return new_pacjent
    except Exception as e:
        logger.error("Error importing pacjent %s %s: %s", pacjent_data.imie, pacjent_data.nazwisko, str(e), exc_info=True)
        raise

def core_update_pacjent(db: Session, id_pacjenta: int, pacjent_data: BaseModel): # BaseModel, żeby mógł przyjmować PacjentCreateForm i PacjentUpdate
    try:
        logger.info("Updating pacjent with ID: %d", id_pacjenta)
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
        logger.info("Pacjent with ID %d updated successfully", id_pacjenta)
        return existing_pacjent
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error updating pacjent with ID %d: %s", id_pacjenta, str(e), exc_info=True)
        raise

def update_pacjent(db: Session, id_pacjenta: int, pacjent_data: PacjentUpdate):
    return core_update_pacjent(db, id_pacjenta, pacjent_data)

def create_pacjent_form(db: Session, id_pacjenta: int, pacjent_data: PacjentCreateForm):
    return core_update_pacjent(db, id_pacjenta, pacjent_data)

def get_recent_pacjenci(db: Session, id_uzytkownika: int, limit: int = 10):
    try:
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
        logger.info("Retrieved %d recent pacjenci for user ID: %d", len(pacjent_list), id_uzytkownika)
        return pacjent_list
    except Exception as e:
        logger.error("Error retrieving recent pacjenci for user ID %d: %s", id_uzytkownika, str(e), exc_info=True)
        raise

def get_recently_created_pacjenci(db: Session, limit: int = 10):
    try:
        pacjent_list = (
            db.query(Pacjent)
            .order_by(Pacjent.Created.desc())
            .limit(limit)
            .all()
        )
        logger.info("Retrieved %d recently created pacjenci", len(pacjent_list))
        return pacjent_list
    except Exception as e:
        logger.error("Error retrieving recently created pacjenci: %s", str(e), exc_info=True)
        raise

def delete_pacjent(db: Session, id_pacjenta: int):
    try:
        pacjent = get_pacjent_by_id(db, id_pacjenta)
        db.delete(pacjent)
        db.commit()
        logger.info("Pacjent with ID %d deleted successfully", id_pacjenta)
        return {"detail": f"Pacjent with ID {id_pacjenta} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error deleting pacjent with ID %d: %s", id_pacjenta, str(e), exc_info=True)
        raise

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
                field = field.strip()
                value = value.strip()
                if not value:  # Skip if value is empty
                    continue
                filter_params[field] = value

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
                # TODO: zapytać mamę, Julę, czy mogą wybierać konkretną datę, a nie rok
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
            elif isinstance(column_to_filter.type, JSONB):
                # JSONB type - handle array containment
                try:
                    # Try to parse as JSON array
                    parsed_value = json.loads(value_str)
                    if isinstance(parsed_value, list):
                        if len(parsed_value) == 0:
                            # Empty array - check for exact match with empty array
                            query = query.filter(column_to_filter == [])
                        else:
                            # Check if the JSONB array contains all the specified values
                            for val in parsed_value:
                                query = query.filter(column_to_filter.contains([val]))
                    else:
                        # Single value - check if array contains it
                        query = query.filter(column_to_filter.contains([parsed_value]))
                    continue
                except (json.JSONDecodeError, TypeError):
                    # If JSON parsing fails, treat the entire value_str as a single element
                    query = query.filter(column_to_filter.contains([value_str]))
                    continue
            else:
                # String type - check for comma-separated values
                if ',' in value_str:
                    values = [v.strip() for v in value_str.split(',') if v.strip()]
                    if values:
                        or_conditions = [column_to_filter == v for v in values]
                        query = query.filter(or_(*or_conditions))
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
    try:
        query = db.query(Pacjent)
        query = search_pacjenci(query, search_term)
        query = filter_pacjenci(query, filters)
        query = sort_pacjenci(query, sort_by, sort_direction)
        logger.debug("Retrieving paginated pacjent list (sort_by=%s, sort_direction=%s, search_term=%s, filters=%s)", sort_by, sort_direction, search_term, filters)
        return paginate(query)
    except Exception as e:
        logger.error("Error retrieving all pacjenci: %s", str(e), exc_info=True)
        raise