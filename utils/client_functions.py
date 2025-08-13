
from db_models.client_data import Pacjent
from schemas.client_schemas import ClientCreate
from sqlalchemy.orm.session import Session
from auth.hashing import Hash
from datetime import datetime
from fastapi import HTTPException, status

def create_client(db: Session, client_data: ClientCreate):
    # Convert to dict with DB column names
    data_dict = client_data.model_dump(by_alias = True, exclude_unset = True)

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
    new_client = Pacjent(**data_dict)
    
    db.add(new_client)
    db.commit()
    db.refresh(new_client)
    return new_client
