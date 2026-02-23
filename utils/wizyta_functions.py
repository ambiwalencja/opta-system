
from fastapi import HTTPException, status
from datetime import datetime
from sqlalchemy import func, distinct
# from sqlalchemy.orm import aliased
from sqlalchemy.orm.session import Session
import logging

from db_models.client_data import Pacjent, WizytaIndywidualna

from schemas.wizyta_schemas import BaseModel, WizytaIndywidualnaCreate, WizytaIndywidualnaImport, WizytaIndywidualnaDisplay
from utils.validation import validate_choice, validate_choice_fields
from utils.pacjent_functions import get_pacjent_by_id

logger = logging.getLogger("opta_system_logger")


def core_save_wizyta(db: Session, wizyta_data: BaseModel):
    try:
        # logger.info("Creating wizyta for pacjent: %d", wizyta_data.id_pacjenta)
        validate_choice(db, "Typ_wizyty", wizyta_data.typ_wizyty)
        logger.debug("Typ_wizyty validation passed: %s", wizyta_data.typ_wizyty)

        data_dict = wizyta_data.model_dump(by_alias = True, exclude_unset = True)

        data_dict["Created"] = datetime.now()
        data_dict["Last_modified"] = datetime.now()
        
        new_wizyta = WizytaIndywidualna(**data_dict)
        
        db.add(new_wizyta)
        db.commit()
        db.refresh(new_wizyta)
        logger.info("Wizyta created with ID: %d", new_wizyta.ID_wizyty)

        pacjent = get_pacjent_by_id(db, new_wizyta.ID_pacjenta)
        pacjent.Data_ostatniej_wizyty = new_wizyta.Data_wizyty
        
        db.add(pacjent)
        db.commit()
        db.refresh(pacjent)
        logger.info("Pacjent last visit date updated for ID: %d", pacjent.ID_pacjenta)

        return new_wizyta
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error creating wizyta: %s", str(e), exc_info=True)
        raise

def create_wizyta(db: Session, wizyta_data: WizytaIndywidualnaCreate):
    try:
        # logger.info("create_wizyta called for pacjent: %d", wizyta_data.id_pacjenta)
        result = core_save_wizyta(db, wizyta_data)
        logger.info("Wizyta created successfully for pacjent: %d", wizyta_data.id_pacjenta)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error in create_wizyta: %s", str(e), exc_info=True)
        raise

def import_wizyta(db: Session, wizyta_data: WizytaIndywidualnaImport):
    try:
        # logger.info("Importing wizyta for pacjent: %d", wizyta_data.id_pacjenta)
        result = core_save_wizyta(db, wizyta_data)
        logger.info("Wizyta imported successfully for pacjent: %d", wizyta_data.id_pacjenta)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error in import_wizyta: %s", str(e), exc_info=True)
        raise

def get_wizyta_by_id(db: Session, id_wizyty: int):
    try:
        # logger.info("Retrieving wizyta with ID: %d", id_wizyty)
        wizyta = db.query(WizytaIndywidualna).filter(WizytaIndywidualna.ID_wizyty == id_wizyty).first()
        if not wizyta:
            logger.warning("Wizyta not found with ID: %d", id_wizyty)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Wizyta with ID {id_wizyty} not found")
        logger.debug("Wizyta retrieved with ID: %d", id_wizyty)
        return wizyta
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error retrieving wizyta with ID %d: %s", id_wizyty, str(e), exc_info=True)
        raise

def update_wizyta(db: Session, id_wizyty: int, wizyta_data: BaseModel):
    try:
        wizyta = get_wizyta_by_id(db, id_wizyty)

        if hasattr(wizyta_data, 'typ_wizyty') and wizyta_data.typ_wizyty is not None:
            # logger.debug("Validating Typ_wizyty: %s", wizyta_data.typ_wizyty)
            validate_choice(db, "Typ_wizyty", wizyta_data.typ_wizyty)

        data_dict = wizyta_data.model_dump(by_alias = True, exclude_unset = True)
        logger.debug("Updating wizyta fields: %s", data_dict.keys())
        data_dict["Last_modified"] = datetime.now()

        for key, value in data_dict.items():
            setattr(wizyta, key, value)

        db.commit()
        db.refresh(wizyta)
        logger.info("Wizyta with ID %d updated", id_wizyty)

        # If Data_wizyty or ID_pacjenta changed, update pacjent's Last_wizyta field
        if 'Data_wizyty' in data_dict or 'ID_pacjenta' in data_dict:
            logger.debug("Updating pacjent last visit date for wizyta: %d", id_wizyty)
            pacjent = get_pacjent_by_id(db, wizyta.ID_pacjenta)
            pacjent.Data_ostatniej_wizyty = wizyta.Data_wizyty
            
            db.commit()
            db.refresh(pacjent)
            logger.info("Pacjent last visit date updated for ID: %d", pacjent.ID_pacjenta)

        return wizyta
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error updating wizyta with ID %d: %s", id_wizyty, str(e), exc_info=True)
        raise

def delete_wizyta(db: Session, id_wizyty: int):
    try:
        # logger.info("Deleting wizyta with ID: %d", id_wizyty)
        wizyta = get_wizyta_by_id(db, id_wizyty)
        db.delete(wizyta)
        db.commit()
        logger.info("Wizyta deleted successfully with ID: %d", id_wizyty)
        return {"detail": f"Wizyta with ID {id_wizyty} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error deleting wizyta with ID %d: %s", id_wizyty, str(e), exc_info=True)
        raise


def get_recent_wizyty(db: Session, limit: int = None):
    try:
        wizyty = db.query(WizytaIndywidualna).order_by(WizytaIndywidualna.Data_wizyty.desc())
        if limit is not None:
            wizyty = wizyty.limit(limit)
        wizyty = wizyty.all()
        logger.debug("Recent wizyty retrieved with limit: %d", limit)
        return wizyty
    except Exception as e:
        logger.error("Error retrieving recent wizyty: %s", str(e), exc_info=True)
        raise

def get_recent_wizyty_for_pacjent(db: Session, id_pacjenta: int, limit: int = None):
    try:
        wizyty = db.query(WizytaIndywidualna).filter(WizytaIndywidualna.ID_pacjenta == id_pacjenta).order_by(WizytaIndywidualna.Data_wizyty.desc())
        if limit is not None:
            wizyty = wizyty.limit(limit)
        wizyty = wizyty.all()
        logger.debug("Recent wizyty retrieved for pacjent with ID: %d and limit: %d", id_pacjenta, limit)
        return wizyty
    except Exception as e:
        logger.error("Error retrieving recent wizyty for pacjent with ID %d and limit %d: %s", id_pacjenta, limit, str(e), exc_info=True)
        raise

def get_recent_wizyty_for_user(db: Session, id_uzytkownika: int, limit: int = None):
    try:
        logger.info("Retrieving recent wizyty for user with ID: %d and limit: %d", id_uzytkownika, limit)
        wizyty = db.query(WizytaIndywidualna).filter(WizytaIndywidualna.ID_uzytkownika == id_uzytkownika).order_by(WizytaIndywidualna.Data_wizyty.desc())
        if limit is not None:
            wizyty = wizyty.limit(limit)
        wizyty = wizyty.all()
        logger.debug("Recent wizyty retrieved for user with ID: %d and limit: %d", id_uzytkownika, limit)
        return wizyty
    except Exception as e:
        logger.error("Error retrieving recent wizyty for user with ID %d and limit %d: %s", id_uzytkownika, limit, str(e), exc_info=True)
        raise

def count_wizyty_for_pacjent(db: Session, id_pacjenta: int):
    try:
        wizyty_count = db.query(
            func.count(WizytaIndywidualna.ID_wizyty),
            WizytaIndywidualna.Typ_wizyty
        ).filter(WizytaIndywidualna.ID_pacjenta == id_pacjenta
        ).group_by(WizytaIndywidualna.Typ_wizyty).all()
        logger.debug("Count of wizyty for pacjent with ID %d: %d", id_pacjenta, len(wizyty_count))
        result = {typ: count for count, typ in wizyty_count}
        return result
    except Exception as e:
        logger.error("Error counting wizyty for pacjent with ID %d: %s", id_pacjenta, str(e), exc_info=True)
        raise