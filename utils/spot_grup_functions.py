from fastapi import HTTPException, status
from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm.session import Session
from typing import Optional
import logging

from db_models.client_data import Grupa, SpotkanieGrupowe, UczestnikGrupy, obecni_uczestnicy_spotkania, Pacjent
from schemas.spot_grup_schemas import  SpotkanieGrupoweCreate, SpotkanieGrupoweUpdate

logger = logging.getLogger("opta_system_logger")

def get_spotkanie_by_id(db: Session, id_spotkania: int):
    try:
        
        spotkanie = db.query(SpotkanieGrupowe).filter(SpotkanieGrupowe.ID_spotkania == id_spotkania).first()
        if not spotkanie:
            logger.warning("Spotkanie grupowe with ID %d not found", id_spotkania)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Spotkanie grupowe with ID {id_spotkania} not found")
        obecni_count = db.query(func.count(obecni_uczestnicy_spotkania.c.ID_uczestnika_grupy)).filter(obecni_uczestnicy_spotkania.c.ID_spotkania == id_spotkania).scalar()
        spotkanie.Obecni_uczestnicy_count = obecni_count
        grupa = db.query(Grupa).filter(Grupa.ID_grupy == spotkanie.ID_grupy).first()
        spotkanie.Nazwa_grupy = grupa.Nazwa_grupy
        # Get participants with their pacjent details
        obecni_uczestnicy_list = db.query(
            UczestnikGrupy.ID_uczestnika_grupy,
            Pacjent.ID_pacjenta,
            Pacjent.Imie,
            Pacjent.Nazwisko
        ).join(Pacjent).join( # w join pacjent nie ma "on" - ale to dziła dobrze
            obecni_uczestnicy_spotkania,
            UczestnikGrupy.ID_uczestnika_grupy == obecni_uczestnicy_spotkania.c.ID_uczestnika_grupy
        ).filter(
            obecni_uczestnicy_spotkania.c.ID_spotkania == id_spotkania
        ).all()
        spotkanie.Obecni_uczestnicy = [
            {
                "ID_uczestnika_grupy": id_uczestnika,
                "ID_pacjenta": id_pacjenta,
                "Imie": imie,
                "Nazwisko": nazwisko
            }
            for id_uczestnika, id_pacjenta, imie, nazwisko in obecni_uczestnicy_list
        ]
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
        data_dict.update({
            "Created": datetime.now(),
            "Last_modified": datetime.now(),
            "ID_uzytkownika": id_uzytkownika
        })
        
        new_spotkanie = SpotkanieGrupowe(**data_dict)
        
        id_list = spotkanie_data.obecni_uczestnicy or []
        if id_list:
            # 1. Fetch all matching participants in ONE query
            participants = db.query(UczestnikGrupy).filter(
                UczestnikGrupy.ID_uczestnika_grupy.in_(id_list),
                UczestnikGrupy.ID_grupy == spotkanie_data.id_grupy
            ).all()

            # 2. Validation: Check if we found everyone
            if len(participants) != len(set(id_list)):
                found_ids = {p.ID_uczestnika_grupy for p in participants}
                missing_ids = set(id_list) - found_ids
                logger.warning("Participants missing or wrong group: %s", missing_ids)
                raise HTTPException(
                    status_code=404, 
                    detail=f"Participants {missing_ids} not found or belong to another group"
                )
            # 3. Assign the full list at once
            new_spotkanie.obecni_uczestnicy = participants

        db.add(new_spotkanie)
        db.commit()
        db.refresh(new_spotkanie)
        
        logger.info("Spotkanie grupowe created with ID: %d", new_spotkanie.ID_spotkania)
        return new_spotkanie

    except HTTPException:
        db.rollback() # Always rollback on known errors
        raise
    except Exception as e:
        db.rollback() # Always rollback on unexpected errors
        logger.error("Error creating spotkanie grupowe: %s", str(e), exc_info=True)
        raise

def update_spotkanie_grupowe(db: Session, id_spotkania: int, spotkanie_data: SpotkanieGrupoweUpdate):
    try:
        logger.info("Updating spotkanie grupowe with ID: %d", id_spotkania)
        spotkanie = db.query(SpotkanieGrupowe).filter(SpotkanieGrupowe.ID_spotkania == id_spotkania).first()
        if not spotkanie:
            raise HTTPException(status_code=404, detail="Spotkanie not found")
        
        data_dict = spotkanie_data.model_dump(by_alias=True, exclude={'obecni_uczestnicy'}, exclude_unset=True)
        data_dict["Last_modified"] = datetime.now()

        for key, value in data_dict.items():
            setattr(spotkanie, key, value)
        
        # relationship update
        if spotkanie_data.obecni_uczestnicy is not None:
            id_list = spotkanie_data.obecni_uczestnicy
            
            new_participants = db.query(UczestnikGrupy).filter(
                UczestnikGrupy.ID_uczestnika_grupy.in_(id_list),
                UczestnikGrupy.ID_grupy == spotkanie.ID_grupy
            ).all()

            # Validation
            if len(new_participants) != len(set(id_list)):
                found_ids = {p.ID_uczestnika_grupy for p in new_participants}
                missing_ids = set(id_list) - found_ids
                raise HTTPException(status_code=400, detail=f"Invalid participant IDs: {missing_ids}")

            # OVERWRITE the relationship. 
            # SQLAlchemy automatically handles the deletes/inserts in the association table.
            spotkanie.obecni_uczestnicy = new_participants

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

