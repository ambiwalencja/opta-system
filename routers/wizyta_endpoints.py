from sqlalchemy.orm.session import Session
from fastapi import APIRouter, Depends, Query as FastapiQuery #, HTTPException, status
import logging
from typing import Optional


from auth.oauth2 import get_user_from_token
from db.db_connect import get_db
from db_models.user_data import User
from schemas.user_schemas import UserSignIn
from schemas.wizyta_schemas import (WizytaIndywidualnaCreate, 
                                    WizytaIndywidualnaDisplay, 
                                    WizytaIndywidualnaUpdate,
                                    WizytaIndywidualnaDisplayDetails)
from utils import wizyta_functions

logger = logging.getLogger("opta_system_logger")

router = APIRouter(
    prefix="/wizyta",
    tags=["wizyta"],
    responses={404: {"description": "Not found"}},
)

@router.get('/get/{id_wizyty}')
def get_wizyta_indywidualna(id_wizyty: int, 
                            db: Session = Depends(get_db), 
                            current_user: User = Depends(get_user_from_token("access_token"))):
    logger.info("User %s retrieving wizyta: %d", current_user.Username, id_wizyty)
    return wizyta_functions.get_wizyta_by_id(db, id_wizyty)

@router.post('/create', response_model=WizytaIndywidualnaDisplay)
def create_wizyta_indywidualna(request: WizytaIndywidualnaCreate, 
                               db: Session = Depends(get_db), 
                               current_user: User = Depends(get_user_from_token("access_token"))):
    logger.info("User %s creating wizyta for pacjent: %d", current_user.Username, request.id_pacjenta)
    return wizyta_functions.create_wizyta(db, request)

@router.put('/update/{id_wizyty}', response_model=WizytaIndywidualnaDisplay)
def update_wizyta_indywidualna(id_wizyty: int, 
                               request: WizytaIndywidualnaUpdate, 
                               db: Session = Depends(get_db), 
                               current_user: User = Depends(get_user_from_token("access_token"))):
    logger.info("User %s updating wizyta: %d", current_user.Username, id_wizyty)
    return wizyta_functions.update_wizyta(db, id_wizyty, request)

@router.delete('/delete/{id_wizyty}')
def delete_wizyta_indywidualna(id_wizyty: int, 
                               db: Session = Depends(get_db), 
                               current_user: User = Depends(get_user_from_token("access_token"))):
    logger.info("User %s deleting wizyta: %d", current_user.Username, id_wizyty)
    return wizyta_functions.delete_wizyta(db, id_wizyty)

@router.get('/recent_wizyty_for_pacjent', response_model=list[WizytaIndywidualnaDisplay]    )
def show_recent_wizyty_for_pacjent(id_pacjenta: Optional[int] = FastapiQuery(None, description="ID of the pacjent to show wizyty for"), 
                                   limit: Optional[int] = FastapiQuery(None, description="Optional limit for recent wizyty"),
                                   db: Session = Depends(get_db), 
                                   current_user: UserSignIn = Depends(get_user_from_token("access_token"))):
    '''Show recent wizyty for the pacjent, with optional limit'''
    logger.info("User %s viewing recent wizyty for pacjent with ID: %d and limit: %s", current_user.Username, id_pacjenta, limit)
    wizyty = wizyta_functions.get_recent_wizyty_for_pacjent(db, id_pacjenta, limit)
    return wizyty

@router.get('/detailed_wizyty_for_pacjent', response_model=list[WizytaIndywidualnaDisplayDetails])
def show_recent_detailed_wizyty_for_pacjent(id_pacjenta: Optional[int] = FastapiQuery(None, description="ID of the pacjent to show wizyty for"), 
                                   limit: Optional[int] = FastapiQuery(None, description="Optional limit for recent wizyty"),
                                   db: Session = Depends(get_db), 
                                   current_user: UserSignIn = Depends(get_user_from_token("access_token"))):
    '''Show detailed recent wizyty for the pacjent, with optional limit'''
    logger.info("User %s viewing detailed recent wizyty for pacjent with ID: %d and limit: %s", current_user.Username, id_pacjenta, limit)
    wizyty = wizyta_functions.get_recent_wizyty_for_pacjent(db, id_pacjenta, limit)
    return wizyty

@router.get('/wizyty_counts_for_pacjent')
def show_wizyty_counts_for_pacjent(id_pacjenta: int, 
                                   db: Session = Depends(get_db), 
                                   current_user: UserSignIn = Depends(get_user_from_token("access_token"))):
    '''Show counts of wizyty for the pacjent, grouped by typ_wizyty'''
    logger.info("User %s viewing wizyty counts for pacjent with ID: %d", current_user.Username, id_pacjenta)
    counts = wizyta_functions.count_wizyty_for_pacjent(db, id_pacjenta)
    return counts