
from fastapi import HTTPException, status
from datetime import datetime
# from sqlalchemy import func, distinct
# from sqlalchemy.orm import aliased
from sqlalchemy.orm.session import Session

# from auth.hashing import Hash
from db_models.client_data import Pacjent, WizytaIndywidualna #, Grupa
# from db_models.config import PossibleValues
# from db_models.user_data import User
from schemas.pacjent_schemas import (
    BaseModel # , CreatePacjentBasic, CreatePacjentForm, DisplayPacjent, 
    # UpdatePacjent, ImportPacjent
)
from schemas.wizyta_schemas import CreateWizytaIndywidualna, ImportWizytaIndywidualna, DisplayWizytaIndywidualna
# from schemas.grupa_schemas import CreateGrupa, DisplayGrupa
from utils.validation import validate_choice, validate_choice_fields
from utils.pacjent_functions import get_pacjent_by_id

def core_save_wizyta(db: Session, wizyta_data: BaseModel):
    # 1. Dynamic validation of typ wizyty
    validate_choice(db, "Typ_wizyty", wizyta_data.typ_wizyty) # ???

    # 2. Convert to dict with DB column names
    data_dict = wizyta_data.model_dump(by_alias = True, exclude_unset = True)

    # 3. Add backend-generated fields
    data_dict["Created"] = datetime.now()
    data_dict["Last_modified"] = datetime.now()
    
    # 4. Create SQLAlchemy object
    new_wizyta = WizytaIndywidualna(**data_dict)
    
    # 5. actually add to DB
    db.add(new_wizyta)
    db.commit()
    db.refresh(new_wizyta)

    # 6. update pacjent's Last_wizyta field
    pacjent = get_pacjent_by_id(db, new_wizyta.ID_pacjenta)
    pacjent.Data_ostatniej_wizyty = new_wizyta.Data
    
    # 7. commit pacjent update
    db.add(pacjent)
    db.commit()
    db.refresh(pacjent)

    return new_wizyta

def create_wizyta(db: Session, wizyta_data: CreateWizytaIndywidualna):
    return core_save_wizyta(db, wizyta_data)

def import_wizyta(db: Session, wizyta_data: ImportWizytaIndywidualna):
    return core_save_wizyta(db, wizyta_data)

def get_wizyta_by_id(db: Session, id_wizyty: int):
    wizyta = db.query(WizytaIndywidualna).filter(WizytaIndywidualna.ID_wizyty == id_wizyty).first()
    if not wizyta:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Wizyta with ID {id_wizyty} not found")
    return wizyta