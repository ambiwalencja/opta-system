from fastapi import HTTPException, status
from datetime import datetime
from sqlalchemy import func, distinct
from sqlalchemy.orm import aliased
from sqlalchemy.orm.session import Session

from auth.hashing import Hash
from db_models.client_data import Pacjent, WizytaIndywidualna #, Grupa
# from db_models.config import PossibleValues
# from db_models.user_data import User
from schemas.pacjent_schemas import (
    BaseModel, CreatePacjentBasic, CreatePacjentForm, # DisplayPacjent, 
    UpdatePacjent, ImportPacjent
)
# from schemas.wizyta_schemas import CreateWizytaIndywidualna, DisplayWizytaIndywidualna
# from schemas.grupa_schemas import CreateGrupa, DisplayGrupa
from utils.validation import validate_choice, validate_choice_fields


def get_pacjent_by_id(db: Session, id_pacjenta: int):
    pacjent = db.query(Pacjent).filter(Pacjent.ID_pacjenta == id_pacjenta).first()
    if not pacjent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Pacjent with ID {id_pacjenta} not found")
    return pacjent

def check_pacjent_duplicates(db: Session, pacjent_data: CreatePacjentBasic):
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

def create_pacjent_basic(db: Session, pacjent_data: CreatePacjentBasic, id_uzytkownika: int):
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

def import_pacjent(db: Session, pacjent_data: ImportPacjent, id_uzytkownika: int):
    # 1. Check for duplicates
    check_pacjent_duplicates(db, pacjent_data)
    # 2. Dynamic validation of all choice fields
    validate_choice_fields(db, pacjent_data)
    # 3. Convert to dict with DB column names
    data_dict = pacjent_data.model_dump(by_alias = True, exclude_unset = True)

    # 4. Add backend-generated fields
    data_dict["Created"] = datetime.now()
    data_dict["Last_modified"] = datetime.now()
    data_dict["ID_uzytkownika"] = id_uzytkownika

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
    new_pacjent = Pacjent(**data_dict)
    # 7. actually add to DB
    db.add(new_pacjent)
    db.commit()
    db.refresh(new_pacjent)
    return new_pacjent

def core_update_pacjent(db: Session, id_pacjenta: int, pacjent_data: BaseModel): # BaseModel, żeby mógł przyjmować CreatePacjentForm i UpdatePacjent
    # 1. Check that pacjent exists and find it
    existing_pacjent = db.query(Pacjent).filter(Pacjent.ID_pacjenta == id_pacjenta).first()
    if not existing_pacjent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Client with ID {id_pacjenta} does not exist')
    
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

def update_pacjent(db: Session, id_pacjenta: int, pacjent_data: UpdatePacjent):
    return core_update_pacjent(db, id_pacjenta, pacjent_data)

def create_pacjent_form(db: Session, id_pacjenta: int, pacjent_data: CreatePacjentForm):
    return core_update_pacjent(db, id_pacjenta, pacjent_data)

def get_recent_pacjenci(db: Session, id_uzytkownika: int, limit: int = 10):
    # Create an alias for WizytaIndywidualna to use in the subquery
    WizytaAlias = aliased(WizytaIndywidualna)
    LatestWizyta = aliased(WizytaIndywidualna)

    # Subquery to get the top 10 patient IDs and their latest visit dates
    latest_visits_subquery = (
        db.query(
            WizytaAlias.ID_pacjenta,
            # func.max(WizytaAlias.Data).label('latest_visit_date'),
            func.max(WizytaAlias.ID_wizyty).label('latest_visit_id')
        )
        .filter(WizytaAlias.ID_uzytkownika == id_uzytkownika)
        .group_by(WizytaAlias.ID_pacjenta)
        .order_by(func.max(WizytaAlias.Data).desc())
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
            LatestWizyta.Data          # Use the alias for selection
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
            # (LatestWizyta.Data == latest_visits_subquery.c.latest_visit_date)
        )
        .filter(LatestWizyta.ID_uzytkownika == id_uzytkownika)
        .order_by(LatestWizyta.Data.desc())
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

