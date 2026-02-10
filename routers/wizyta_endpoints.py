from sqlalchemy.orm.session import Session
from fastapi import APIRouter, Depends #, HTTPException, status
import logging

from auth.oauth2 import get_user_from_token
from db.db_connect import get_db
from db_models.user_data import User
from schemas.wizyta_schemas import WizytaIndywidualnaCreate, WizytaIndywidualnaDisplay, WizytaIndywidualnaUpdate
from utils import wizyta_functions

logger = logging.getLogger("opta_system_logger")

router = APIRouter(
    prefix="/wizyta",
    tags=["wizyta"],
    responses={404: {"description": "Not found"}},
)

@router.get('/get/{id_wizyty}')
def get_wizyta_indywidualna(id_wizyty: int, db: Session = Depends(get_db), current_user: User = Depends(get_user_from_token("access_token"))):
    logger.info("User %s retrieving wizyta: %d", current_user.Username, id_wizyty)
    return wizyta_functions.get_wizyta_by_id(db, id_wizyty)

@router.post('/create', response_model=WizytaIndywidualnaDisplay)
def create_wizyta_indywidualna(request: WizytaIndywidualnaCreate, db: Session = Depends(get_db), current_user: User = Depends(get_user_from_token("access_token"))):
    logger.info("User %s creating wizyta for pacjent: %d", current_user.Username, request.id_pacjenta)
    return wizyta_functions.create_wizyta(db, request)

@router.put('/update/{id_wizyty}', response_model=WizytaIndywidualnaDisplay)
def update_wizyta_indywidualna(id_wizyty: int, request: WizytaIndywidualnaUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_user_from_token("access_token"))):
    logger.info("User %s updating wizyta: %d", current_user.Username, id_wizyty)
    return wizyta_functions.update_wizyta(db, id_wizyty, request)

@router.delete('/delete/{id_wizyty}')
def delete_wizyta_indywidualna(id_wizyty: int, db: Session = Depends(get_db), current_user: User = Depends(get_user_from_token("access_token"))):
    logger.info("User %s deleting wizyta: %d", current_user.Username, id_wizyty)
    return wizyta_functions.delete_wizyta(db, id_wizyty)