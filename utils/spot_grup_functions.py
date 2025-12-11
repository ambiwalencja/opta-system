
from fastapi import HTTPException, status
from datetime import datetime
from sqlalchemy.orm.session import Session

from db_models.client_data import Pacjent, WizytaIndywidualna, Grupa, SpotkanieGrupowe, UczestnikGrupy

from schemas.wizyta_schemas import BaseModel, WizytaIndywidualnaCreate, WizytaIndywidualnaImport, WizytaIndywidualnaDisplay
from schemas.spot_grup_schemas import BaseModel, SpotkanieGrupoweCreate, SpotkanieGrupoweUpdate

from utils.validation import validate_choice, validate_choice_fields
from utils.pacjent_functions import get_pacjent_by_id


def get_spotkanie_by_id(db: Session, id_spotkania: int):
    spotkanie = db.query(SpotkanieGrupowe).filter(SpotkanieGrupowe.ID_spotkania == id_spotkania).first()
    if not spotkanie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Spotkanie grupowe with ID {id_spotkania} not found")
    return spotkanie

def create_spotkanie_grupowe(db: Session, spotkanie_data: SpotkanieGrupoweCreate, id_uzytkownika: int):
    data_dict = spotkanie_data.model_dump(by_alias=True, exclude={'obecni_uczestnicy'})
    data_dict["Created"] = datetime.now()
    data_dict["Last_modified"] = datetime.now()
    data_dict["ID_uzytkownika"] = id_uzytkownika
    new_spotkanie = SpotkanieGrupowe(**data_dict)
    
    id_obecnych_uczestnikow = spotkanie_data.obecni_uczestnicy or []
    if id_obecnych_uczestnikow:
        uczestnik_to_add = db.query(UczestnikGrupy).filter(UczestnikGrupy.ID_uczestnika_grupy.in_(id_obecnych_uczestnikow)).all()
        # TODO; dodać sprawdzenie, czy uczestnik o danym id na pewno jest w tej grupie
        new_spotkanie.obecni_uczestnicy.extend(uczestnik_to_add)
    
    db.add(new_spotkanie)
    db.commit()
    db.refresh(new_spotkanie)

    return new_spotkanie

def update_spotkanie_grupowe(db: Session, id_spotkania: int, spotkanie_data: SpotkanieGrupoweUpdate):
    data_dict = spotkanie_data.model_dump(by_alias=True, exclude={'obecni_uczestnicy'}, exclude_unset=True)
    data_dict["Last_modified"] = datetime.now()
    spotkanie = get_spotkanie_by_id(db, id_spotkania)

    for key, value in data_dict.items():
        setattr(spotkanie, key, value)
    
    db.commit()
    db.refresh(spotkanie)
    return spotkanie

def delete_spotkanie_grupowe(db: Session, id_spotkania: int):
    spotkanie = get_spotkanie_by_id(db, id_spotkania)
    db.delete(spotkanie)
    db.commit()
    return {"detail": f"Spotkanie grupowe with ID {id_spotkania} deleted successfully"}

