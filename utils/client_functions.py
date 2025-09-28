
from db_models.client_data import Pacjent
from db_models.config import PossibleValues
from schemas.client_schemas import CreatePacjent
from sqlalchemy.orm.session import Session
from auth.hashing import Hash
from datetime import datetime
from fastapi import HTTPException, status

def check_pacjent_duplicates(db: Session, pacjent_data: CreatePacjent):
    # check for duplicates - phone, email, fullname+address
    if pacjent_data.telefon and db.query(Pacjent).filter(Pacjent.Telefon == pacjent_data.telefon).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Client with phone number {pacjent_data.telefon} already exists')
    if pacjent_data.email and db.query(Pacjent).filter(Pacjent.Email == pacjent_data.email).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Client with email {pacjent_data.email} already exists')
    if db.query(Pacjent).filter(
            Pacjent.Imie == pacjent_data.imie,
            Pacjent.Nazwisko == pacjent_data.nazwisko,
            Pacjent.Dzielnica == pacjent_data.dzielnica,
            Pacjent.Ulica == pacjent_data.ulica,
            Pacjent.Nr_domu == pacjent_data.nr_domu
        ).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Client with name {pacjent_data.imie} {pacjent_data.nazwisko} and the same address already exists')

def validate_choice(db: Session, variable_name: str, chosen_value: str):
    variable_with_pv = db.query(PossibleValues).filter(PossibleValues.Variable_name == variable_name).first()
    if not variable_with_pv:
        return  # no restriction for this field → skip validation
    
    if chosen_value not in variable_with_pv.Possible_values:  # dict keys are the valid values
        raise HTTPException(
            status_code=400,
            detail=f"Invalid value '{chosen_value}' for {variable_name}. Allowed: {list(variable_with_pv.Possible_values.keys())}"
        )

def validate_choice_fields(db: Session, pacjent_data: CreatePacjent):
    data_dict = pacjent_data.model_dump(by_alias=True, exclude_unset=True)
    
    for field_name, field_value in data_dict.items():
        if field_value is not None:
            # Check for list fields (korzystanie z pomocy, problemy, zaproponowane wsparcie)
            if isinstance(field_value, list):
                for item in field_value:
                    validate_choice(db, field_name, item)
            else:
                validate_choice(db, field_name, field_value)

def create_pacjent(db: Session, pacjent_data: CreatePacjent):
    # 1. Check for duplicates
    check_pacjent_duplicates(db, pacjent_data)
    # 2. Dynamic validation of all choice fields
    validate_choice_fields(db, pacjent_data)
    # 3. Convert to dict with DB column names
    data_dict = pacjent_data.model_dump(by_alias = True, exclude_unset = True)

    # 4. Add backend-generated fields
    data_dict["Created"] = datetime.now()
    data_dict["Last_modified"] = datetime.now()

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

