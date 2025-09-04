
from db_models.client_data import Pacjent
from db_models.config import PossibleValues
from schemas.client_schemas import CreatePacjent
from sqlalchemy.orm.session import Session
from auth.hashing import Hash
from datetime import datetime
from fastapi import HTTPException, status

def create_pacjent(db: Session, pacjent_data: CreatePacjent):
    # Convert to dict with DB column names
    data_dict = pacjent_data.model_dump(by_alias = True, exclude_unset = True)

    # Add backend-generated fields
    data_dict["Created"] = datetime.now()
    data_dict["Last_modified"] = datetime.now()

    # Conditional cleanup - optional
    if not data_dict.get("Niebieska_karta"):
        data_dict["Niebieska_karta_inicjator"] = None
        data_dict["Grupa_robocza"] = None
        data_dict["Grupa_robocza_sklad"] = None
        data_dict["Plan_pomocy"] = None
        data_dict["Plan_pomocy_opis"] = None
        data_dict["Narzedzia_prawne"] = None
        data_dict["Zawiadomienie"] = None
    
    # Create SQLAlchemy object
    new_pacjent = Pacjent(**data_dict)
    
    db.add(new_pacjent)
    db.commit()
    db.refresh(new_pacjent)
    return new_pacjent

def validate_choice(db: Session, variable_name: str, chosen_value: str):
    variable_with_pv = db.query(PossibleValues).filter(PossibleValues.Variable_name == variable_name).first()
    if not variable_with_pv:
        return  # no restriction for this field → skip validation
    
    if chosen_value not in variable_with_pv.Possible_values:  # dict keys are the valid values
        raise HTTPException(
            status_code=400,
            detail=f"Invalid value '{chosen_value}' for {variable_name}. Allowed: {list(variable_with_pv.Possible_values.keys())}"
        )