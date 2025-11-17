from datetime import datetime
# from fastapi import HTTPException, status
# from sqlalchemy import func, distinct
from sqlalchemy import or_
# from sqlalchemy.orm import aliased
from sqlalchemy.orm.session import Session
from sqlalchemy.orm import joinedload

from auth.hashing import Hash
from db_models.client_data import Grupa, UczestnikGrupy
# from db_models.config import PossibleValues
from db_models.user_data import User
# from schemas.pacjent_schemas import PacjentCreateBasic, PacjentCreateForm, PacjentDisplay, PacjentUpdate
# from schemas.wizyta_schemas import WizytaIndywidualnaCreate, WizytaIndywidualnaDisplay
from schemas.grupa_schemas import (GrupaCreate, GrupaDisplay, 
                                   GrupaUpdate, UczestnikGrupyCreate,
                                   UczestnikGrupyDisplay)
from utils.validation import validate_choice, validate_choice_fields

def get_grupa_by_id(db: Session, id_grupy: int):
    grupa = db.query(Grupa).filter(Grupa.ID_grupy == id_grupy).first()
    if not grupa:
        raise Exception(f"Grupa with ID {id_grupy} not found")
    return grupa

def create_grupa(db: Session, grupa_data: GrupaCreate, id_uzytkownika: int):
    # Validate value of Typ_grupy
    validate_choice(db, "Typ_grupy", grupa_data.typ_grupy)

    # Convert to dict with DB column names
    data_dict = grupa_data.model_dump(by_alias = True, exclude={'prowadzacy'})
    data_dict["Created"] = datetime.now()
    data_dict["Last_modified"] = datetime.now()
    data_dict["ID_uzytkownika"] = id_uzytkownika  # creator

    # Create SQLAlchemy object
    new_grupa = Grupa(**data_dict)
    
    # Fetch the User objects based on the list of IDs
    id_prowadzacych = grupa_data.prowadzacy or []
    if id_prowadzacych:
        # Fetch the User objects WHERE User.id is IN the provided list
        prowadzacy_to_add = db.query(User).filter(User.ID_uzytkownika.in_(id_prowadzacych)).all()
        
        # Assign the relationship using the relationship collection
        new_grupa.prowadzacy.extend(prowadzacy_to_add)
    
    # actually add to DB
    db.add(new_grupa)
    db.commit()
    db.refresh(new_grupa)

    return new_grupa

def get_recently_added_groups(db: Session, limit: int = 10):
    grupa_list = (
        db.query(Grupa)
        .order_by(Grupa.Created.desc())
        .limit(limit)
        .all()
    )
    return grupa_list

def get_groups_for_user(db: Session, id_uzytkownika: int):
    grupa_list = (
        db.query(Grupa)
        .join(Grupa.prowadzacy)  # Join with the User table through the relationship
        .filter(User.ID_uzytkownika == id_uzytkownika)  # Filter by the specific user ID
        .all()
    )
    return grupa_list

def get_current_groups_for_user(db: Session, id_uzytkownika: int):
    current_date = datetime.now().date()
    grupa_list = (
        db.query(Grupa)
        .join(Grupa.prowadzacy)
        .filter(
            User.ID_uzytkownika == id_uzytkownika,
            or_(Grupa.Data_zakonczenia >= current_date, 
                Grupa.Data_zakonczenia == None)
        )
        .all()
    )
    return grupa_list

def update_grupa(db: Session, id_grupy: int, grupa_data: GrupaUpdate, id_uzytkownika: int):
    grupa = get_grupa_by_id(db, id_grupy)

    # Validate value of Typ_grupy
    if hasattr(grupa_data, 'typ_grupy') and grupa_data.typ_grupy is not None:
        validate_choice(db, "Typ_grupy", grupa_data.typ_grupy)

    # Convert to dict with DB column names
    data_dict = grupa_data.model_dump(by_alias = True, exclude_unset=True, exclude={'prowadzacy'})
    data_dict["Last_modified"] = datetime.now()

    # Update fields
    for key, value in data_dict.items():
        setattr(grupa, key, value)

    # Update prowadzacy relationship if provided
    id_prowadzacych = grupa_data.prowadzacy
    if id_prowadzacych is not None:
        # Clear existing relationships
        grupa.prowadzacy.clear()
        
        if id_prowadzacych:
            # Fetch the User objects WHERE User.id is IN the provided list
            prowadzacy_to_add = db.query(User).filter(User.ID_uzytkownika.in_(id_prowadzacych)).all()
            
            # Assign the relationship using the relationship collection
            grupa.prowadzacy.extend(prowadzacy_to_add)

    # Commit changes to DB
    db.commit()
    db.refresh(grupa)
    return grupa

def delete_grupa(db: Session, id_grupy: int):
    grupa = get_grupa_by_id(db, id_grupy)
    db.delete(grupa)
    db.commit()
    return {"detail": f"Grupa with ID {id_grupy} deleted successfully"}

def create_uczestnik_grupy(db: Session, uczestnik_data: UczestnikGrupyCreate):
    data_dict = uczestnik_data.model_dump(by_alias = True)
    data_dict["Created"] = datetime.now()
    data_dict["Last_modified"] = datetime.now()

    new_uczestnik = UczestnikGrupy(**data_dict)

    # grupa_obj = db.query(Grupa).get(data_dict["ID_grupy"])
    # pacjent_obj = db.query(Pacjent).get(data_dict["ID_pacjenta"])
    # if grupa_obj: new_uczestnik.grupa = grupa_obj
    # if pacjent_obj: new_uczestnik.pacjent = pacjent_obj

    db.add(new_uczestnik)
    db.commit()
    db.refresh(new_uczestnik)

    return new_uczestnik
    # uczestnik = (
    #     db.query(UczestnikGrupy)
    #     .options(joinedload(UczestnikGrupy.grupa), joinedload(UczestnikGrupy.pacjent))
    #     .get(new_uczestnik.ID_uczestnika_grupy)
    # )
    # # Return validated Pydantic model (ensures response_model matches and uses aliases)
    # return DisplayUczestnikGrupy.model_validate(uczestnik)
