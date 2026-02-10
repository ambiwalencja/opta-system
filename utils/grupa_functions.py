from datetime import datetime
from fastapi import HTTPException, status
import logging
from sqlalchemy import or_
from sqlalchemy.orm.session import Session
# from sqlalchemy.orm import joinedload
from typing import List

from db_models.client_data import Grupa, UczestnikGrupy, Pacjent
from db_models.user_data import User

from schemas.grupa_schemas import (GrupaCreate, GrupaDisplay, 
                                   GrupaUpdate, UczestnikGrupyCreate,
                                   UczestnikGrupyDisplay, UczestnikGrupyUpdate)
from utils.validation import validate_choice, validate_choice_fields

logger = logging.getLogger("opta_system_logger")

def get_grupa_by_id(db: Session, id_grupy: int):
    try:
        grupa = db.query(Grupa).filter(Grupa.ID_grupy == id_grupy).first()
        if not grupa:
            logger.warning("Grupa with ID %d not found", id_grupy)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Grupa with ID {id_grupy} not found")
        logger.debug("Grupa with ID %d retrieved", id_grupy)
        return grupa
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error retrieving grupa with ID %d: %s", id_grupy, str(e), exc_info=True)
        raise

def _update_prowadzacy_relationship(grupa: Grupa, id_prowadzacych: List[int], db: Session):
    if id_prowadzacych is not None:
        grupa.prowadzacy.clear()
        
        if id_prowadzacych:
            prowadzacy_to_add = db.query(User).filter(User.ID_uzytkownika.in_(id_prowadzacych)).all()
            grupa.prowadzacy.extend(prowadzacy_to_add)

def create_grupa(db: Session, grupa_data: GrupaCreate, id_uzytkownika: int):
    try:
        validate_choice(db, "Typ_grupy", grupa_data.typ_grupy)

        data_dict = grupa_data.model_dump(by_alias = True, exclude={'prowadzacy'})
        data_dict["Created"] = datetime.now()
        data_dict["Last_modified"] = datetime.now()
        data_dict["ID_uzytkownika"] = id_uzytkownika  # creator

        new_grupa = Grupa(**data_dict)
        
        _update_prowadzacy_relationship(new_grupa, grupa_data.prowadzacy, db)

        db.add(new_grupa)
        db.commit()
        db.refresh(new_grupa)

        logger.info("Grupa created successfully with ID: %d", new_grupa.ID_grupy)
        return new_grupa
    except Exception as e:
        logger.error("Error creating grupa: %s", str(e), exc_info=True)
        raise

def get_recently_added_groups(db: Session, limit: int = 10):
    try:
        # logger.info("Retrieving recently added groups (limit: %d)", limit)
        grupa_list = (
            db.query(Grupa)
            .order_by(Grupa.Created.desc())
            .limit(limit)
            .all()
        )
        logger.info("Retrieved %d recently added groups", len(grupa_list))
        return grupa_list
    except Exception as e:
        logger.error("Error retrieving recently added groups: %s", str(e), exc_info=True)
        raise

def get_groups_for_user(db: Session, id_uzytkownika: int):
    try:
        logger.info("Retrieving groups for user ID: %d", id_uzytkownika)
        grupa_list = (
            db.query(Grupa)
            .join(Grupa.prowadzacy)  # Join with the User table through the relationship
            .filter(User.ID_uzytkownika == id_uzytkownika)  # Filter by the specific user ID
            .all()
        )
        logger.info("Retrieved %d groups for user ID: %d", len(grupa_list), id_uzytkownika)
        return grupa_list
    except Exception as e:
        logger.error("Error retrieving groups for user ID %d: %s", id_uzytkownika, str(e), exc_info=True)
        raise

def get_current_groups_for_user(db: Session, id_uzytkownika: int):
    try:
        logger.info("Retrieving current groups for user ID: %d", id_uzytkownika)
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
        logger.info("Retrieved %d current groups for user ID: %d", len(grupa_list), id_uzytkownika)
        return grupa_list
    except Exception as e:
        logger.error("Error retrieving current groups for user ID %d: %s", id_uzytkownika, str(e), exc_info=True)
        raise

def update_grupa(db: Session, id_grupy: int, grupa_data: GrupaUpdate, id_uzytkownika: int):
    try:
        grupa = get_grupa_by_id(db, id_grupy)

        if hasattr(grupa_data, 'typ_grupy') and grupa_data.typ_grupy is not None:
            validate_choice(db, "Typ_grupy", grupa_data.typ_grupy)

        data_dict = grupa_data.model_dump(by_alias = True, exclude_unset=True, exclude={'prowadzacy'})
        data_dict["Last_modified"] = datetime.now()

        for key, value in data_dict.items():
            setattr(grupa, key, value)

        _update_prowadzacy_relationship(grupa, grupa_data.prowadzacy, db)

        db.commit()
        db.refresh(grupa)
        logger.info("Grupa with ID: %d updated successfully", id_grupy)
        return grupa
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error updating grupa with ID %d: %s", id_grupy, str(e), exc_info=True)
        raise

def delete_grupa(db: Session, id_grupy: int):
    try:
        grupa = get_grupa_by_id(db, id_grupy)
        db.delete(grupa)
        db.commit()
        logger.info("Grupa with ID: %d deleted successfully", id_grupy)
        return {"detail": f"Grupa with ID {id_grupy} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error deleting grupa with ID %d: %s", id_grupy, str(e), exc_info=True)
        raise


def check_uczestnik_grupy_duplicates(db: Session, id_grupy: int, id_pacjenta: int):
    try:
        existing_entry = db.query(UczestnikGrupy).filter(
            UczestnikGrupy.ID_grupy == id_grupy,
            UczestnikGrupy.ID_pacjenta == id_pacjenta
        ).first()
        if existing_entry:
            logger.warning("Duplicate uczestnik grupy found for grupa ID: %d, pacjent ID: %d", id_grupy, id_pacjenta)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"UczestnikGrupy with ID_grupy {id_grupy} and ID_pacjenta {id_pacjenta} already exists"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error checking uczestnik grupy duplicates: %s", str(e), exc_info=True)
        raise
    
def create_uczestnik_grupy(db: Session, uczestnik_data: UczestnikGrupyCreate):
    try:
        data_dict = uczestnik_data.model_dump(by_alias = True)
        data_dict["Created"] = datetime.now()
        data_dict["Last_modified"] = datetime.now()
        
        check_uczestnik_grupy_duplicates(db, data_dict["ID_grupy"], data_dict["ID_pacjenta"])
        new_uczestnik = UczestnikGrupy(**data_dict)

        db.add(new_uczestnik)
        db.commit()
        db.refresh(new_uczestnik)

        uczestnik = (
            db.query(UczestnikGrupy)
            # .options(joinedload(UczestnikGrupy.grupa), joinedload(UczestnikGrupy.pacjent))
            .get(new_uczestnik.ID_uczestnika_grupy)
        )
        logger.info("Uczestnik grupy created successfully with ID: %d", new_uczestnik.ID_uczestnika_grupy)
        return UczestnikGrupyDisplay.model_validate(uczestnik)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error creating uczestnik grupy: %s", str(e), exc_info=True)
        raise

def get_uczestnik_grupy_by_id(db: Session, id_uczestnika_grupy: int):
    try:
        uczestnik = db.query(UczestnikGrupy).get(id_uczestnika_grupy)
        if not uczestnik:
            logger.warning("UczestnikGrupy with ID %d not found", id_uczestnika_grupy)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"UczestnikGrupy with ID {id_uczestnika_grupy} not found")
        logger.debug("UczestnikGrupy with ID %d retrieved", id_uczestnika_grupy)
        return uczestnik
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error retrieving uczestnik grupy with ID %d: %s", id_uczestnika_grupy, str(e), exc_info=True)
        raise

def update_uczestnik_grupy(db: Session, id_uczestnika_grupy: int, uczestnik_data: UczestnikGrupyUpdate):
    try:
        uczestnik = get_uczestnik_grupy_by_id(db, id_uczestnika_grupy)

        data_dict = uczestnik_data.model_dump(by_alias = True, exclude_unset=True)
        data_dict["Last_modified"] = datetime.now()

        for key, value in data_dict.items():
            setattr(uczestnik, key, value)

        db.commit()
        db.refresh(uczestnik)
        logger.info("Uczestnik grupy with ID: %d updated successfully", id_uczestnika_grupy)
        return uczestnik
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error updating uczestnik grupy with ID %d: %s", id_uczestnika_grupy, str(e), exc_info=True)
        raise

def delete_uczestnik_grupy(db: Session, id_uczestnika_grupy: int):
    try:
        uczestnik = get_uczestnik_grupy_by_id(db, id_uczestnika_grupy)
        db.delete(uczestnik)
        db.commit()
        logger.info("Uczestnik grupy with ID: %d deleted successfully", id_uczestnika_grupy)
        return {"detail": f"UczestnikGrupy with ID {id_uczestnika_grupy} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error deleting uczestnik grupy with ID %d: %s", id_uczestnika_grupy, str(e), exc_info=True)
        raise

def show_uczestnicy_grupy(db: Session, id_grupy: int):
    try:
        uczestnicy = (
            db.query(UczestnikGrupy)
            #.options(joinedload(UczestnikGrupy.pacjent))
            .filter(UczestnikGrupy.ID_grupy == id_grupy)
            .all()
        )
        logger.info("Retrieved %d uczestnicy for grupa ID: %d", len(uczestnicy), id_grupy)
        return uczestnicy
    except Exception as e:
        logger.error("Error retrieving uczestnicy for grupa ID %d: %s", id_grupy, str(e), exc_info=True)
        raise