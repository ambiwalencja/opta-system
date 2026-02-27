from sqlalchemy.orm.session import Session
from fastapi import APIRouter, Depends, Query as FastapiQuery #, HTTPException, status
import logging

from db.db_connect import get_db
from auth.oauth2 import get_user_from_token
from schemas.pacjent_schemas import PacjentDisplay
# from schemas.wizyta_schemas import WizytaIndywidualnaCreate, WizytaIndywidualnaDisplay
from schemas.grupa_schemas import (GrupaCreate, GrupaDisplay, 
                                   GrupaUpdate, UczestnikGrupyCreate,
                                   UczestnikGrupyDisplay, UczestnikGrupyUpdate)
# from db_models.client_data import Pacjent
from db_models.user_data import User
from utils import grupa_functions


router = APIRouter(
    prefix="/grupa",
    tags=["grupa"],
    responses={404: {"description": "Not found"}},
)

logger = logging.getLogger("opta_system_logger")

@router.get('/', response_model=GrupaDisplay)
def get_grupa(id_grupy: int = FastapiQuery(...), db: Session = Depends(get_db), current_user: User = Depends(get_user_from_token("access_token"))):
    return grupa_functions.get_grupa_by_id(db, id_grupy)

@router.post('/create', response_model=GrupaDisplay)
def create_grupa(request: GrupaCreate, db: Session = Depends(get_db), current_user: User = Depends(get_user_from_token("access_token"))):
    logger.info("User %s creating new grupa with type: %s", current_user.Username, request.typ_grupy)
    return grupa_functions.create_grupa(db, request, current_user.ID_uzytkownika)

@router.put('/update', response_model=GrupaDisplay)
def update_grupa(id_grupy: int = FastapiQuery(...), request: GrupaUpdate = None, db: Session = Depends(get_db), current_user: User = Depends(get_user_from_token("access_token"))):
    logger.info("User %s updating grupa with ID: %d", current_user.Username, id_grupy)
    return grupa_functions.update_grupa(db, id_grupy, request, current_user.ID_uzytkownika)

@router.delete('/delete')
def delete_grupa(id_grupy: int = FastapiQuery(...), db: Session = Depends(get_db), current_user: User = Depends(get_user_from_token("access_token"))):
    logger.info("User %s deleting grupa with ID: %d", current_user.Username, id_grupy)
    return grupa_functions.delete_grupa(db, id_grupy)

@router.get('/all', response_model=list[GrupaDisplay])
def show_all_groups(db: Session = Depends(get_db), current_user: User = Depends(get_user_from_token("access_token"))):
    logger.info("User %s retrieving all groups", current_user.Username)
    return grupa_functions.get_all_groups(db)



@router.post('/uczestnik/create', response_model=UczestnikGrupyDisplay)
def create_uczestnik_grupy(request: UczestnikGrupyCreate, db: Session = Depends(get_db), current_user: User = Depends(get_user_from_token("access_token"))):
    logger.info("User %s creating uczestnik for grupa ID: %d, pacjent ID: %d", current_user.Username, request.id_grupy, request.id_pacjenta)
    return grupa_functions.create_uczestnik_grupy(db, request)

@router.get('/uczestnik', response_model=UczestnikGrupyDisplay)
def get_uczestnik_grupy(id_uczestnika_grupy: int = FastapiQuery(...), db: Session = Depends(get_db), current_user: User = Depends(get_user_from_token("access_token"))):
    return grupa_functions.get_uczestnik_grupy_by_id(db, id_uczestnika_grupy)

@router.put('/uczestnik/update', response_model=UczestnikGrupyDisplay)
def update_uczestnik_grupy(id_uczestnika_grupy: int = FastapiQuery(...), request: UczestnikGrupyUpdate = None, db: Session = Depends(get_db), current_user: User = Depends(get_user_from_token("access_token"))):
    logger.info("User %s updating uczestnik grupy with ID: %d", current_user.Username, id_uczestnika_grupy)
    return grupa_functions.update_uczestnik_grupy(db, id_uczestnika_grupy, request)

@router.delete('/uczestnik/delete')
def delete_uczestnik_grupy(id_uczestnika_grupy: int = FastapiQuery(...), db: Session = Depends(get_db), current_user: User = Depends(get_user_from_token("access_token"))):
    logger.info("User %s deleting uczestnik grupy with ID: %d", current_user.Username, id_uczestnika_grupy)
    return grupa_functions.delete_uczestnik_grupy(db, id_uczestnika_grupy)

@router.get('/uczestnicy', response_model=list[UczestnikGrupyDisplay])
def show_uczestnicy_grupy(id_grupy: int = FastapiQuery(...), db: Session = Depends(get_db), current_user: User = Depends(get_user_from_token("access_token"))):
    logger.info("User %s retrieving uczestnicy for grupa ID: %d", current_user.Username, id_grupy)
    return grupa_functions.show_uczestnicy_grupy(db, id_grupy)