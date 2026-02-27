from fastapi import HTTPException, status
from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm.session import Session
from typing import Optional
import logging

from db_models.client_data import Grupa, SpotkanieGrupowe, UczestnikGrupy, obecni_uczestnicy_spotkania
from schemas.spot_grup_schemas import  SpotkanieGrupoweCreate, SpotkanieGrupoweUpdate

logger = logging.getLogger("opta_system_logger")

def get_spotkanie_by_id(db: Session, id_spotkania: int):
    try:
        spotkanie = db.query(SpotkanieGrupowe).filter(SpotkanieGrupowe.ID_spotkania == id_spotkania).first()
        if not spotkanie:
            logger.warning("Spotkanie grupowe with ID %d not found", id_spotkania)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Spotkanie grupowe with ID {id_spotkania} not found")
        logger.debug("Spotkanie grupowe with ID %d retrieved successfully", id_spotkania)
        return spotkanie
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error retrieving spotkanie grupowe with ID %d: %s", id_spotkania, str(e), exc_info=True)
        raise

def create_spotkanie_grupowe(db: Session, spotkanie_data: SpotkanieGrupoweCreate, id_uzytkownika: int):
    try:
        logger.info("Creating new spotkanie grupowe for user ID: %d", id_uzytkownika)
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
        logger.info("Spotkanie grupowe created successfully with ID: %d", new_spotkanie.ID_spotkania)
        return new_spotkanie
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error creating spotkanie grupowe: %s", str(e), exc_info=True)
        raise

def update_spotkanie_grupowe(db: Session, id_spotkania: int, spotkanie_data: SpotkanieGrupoweUpdate):
    try:
        logger.info("Updating spotkanie grupowe with ID: %d", id_spotkania)
        data_dict = spotkanie_data.model_dump(by_alias=True, exclude={'obecni_uczestnicy'}, exclude_unset=True)
        data_dict["Last_modified"] = datetime.now()
        spotkanie = get_spotkanie_by_id(db, id_spotkania)

        for key, value in data_dict.items():
            setattr(spotkanie, key, value)
        
        db.commit()
        db.refresh(spotkanie)
        logger.info("Spotkanie grupowe with ID %d updated successfully", id_spotkania)
        return spotkanie
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error updating spotkanie grupowe with ID %d: %s", id_spotkania, str(e), exc_info=True)
        raise

def delete_spotkanie_grupowe(db: Session, id_spotkania: int):
    try:
        spotkanie = get_spotkanie_by_id(db, id_spotkania)
        db.delete(spotkanie)
        db.commit()
        logger.info("Spotkanie grupowe with ID %d deleted successfully", id_spotkania)
        return {"detail": f"Spotkanie grupowe with ID {id_spotkania} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error deleting spotkanie grupowe with ID %d: %s", id_spotkania, str(e), exc_info=True)
        raise

def get_all_spotkania_grupowe(db: Session, id_grupy: Optional[int] = None):
    try:
        query = (
            db.query(
                SpotkanieGrupowe,
                func.count(obecni_uczestnicy_spotkania.c.ID_uczestnika_grupy),
                Grupa.Nazwa_grupy
                )
            .outerjoin(obecni_uczestnicy_spotkania) # We use an outer join so that if a meeting has zero participants, it still shows up in your list with a count of 0.
            .outerjoin(Grupa)
            .group_by(SpotkanieGrupowe.ID_spotkania, Grupa.Nazwa_grupy)
        ) #result: list of tuples (SpotkanieGrupowe, count_obecni_uczestnicy) because it's a group_by result
        
        if id_grupy:
            query = query.filter(SpotkanieGrupowe.ID_grupy == id_grupy)
        spotkania = query.all()
        logger.info("All spotkania grupowe retrieved successfully, count: %d", len(spotkania))
        results = []
        for spotkanie, count, nazwa_grupy in spotkania:
            logger.debug("Spotkanie ID: %d, Obecni uczestnicy count: %d, Nazwa grupy: %s", spotkanie.ID_spotkania, count, nazwa_grupy)
            spotkanie.Obecni_uczestnicy_count = count # new parameter added to SpotkanieGrupowe model
            spotkanie.Nazwa_grupy = nazwa_grupy # new parameter added to SpotkanieGrupowe model
            results.append(spotkanie)
        return results
    except Exception as e:
        logger.error("Error retrieving all spotkania grupowe: %s", str(e), exc_info=True)
        raise

