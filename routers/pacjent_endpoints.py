from sqlalchemy.orm.session import Session
from typing import Optional, List
from fastapi import APIRouter, Depends, Query as FastapiQuery
from fastapi_pagination import Page
import logging

from db.db_connect import get_db
from auth.oauth2 import get_user_from_token
from schemas.pacjent_schemas import (PacjentCreateBasic, PacjentCreateForm, 
                                     PacjentDisplay, PacjentUpdate)
from db_models.user_data import User
from utils import pacjent_functions

logger = logging.getLogger("opta_system_logger")


router = APIRouter(
    prefix="/pacjent",
    tags=["pacjent"],
    responses={404: {"description": "Not found"}},
)

@router.post('/create_basic', response_model=PacjentDisplay)
def create_pacjent_1(request: PacjentCreateBasic, db: Session = Depends(get_db), current_user: User = Depends(get_user_from_token("access_token"))):
    logger.info("User %s creating new pacjent (basic form)", current_user.Username)
    return pacjent_functions.create_pacjent_basic(db, request, current_user.ID_uzytkownika)

@router.post('/create_form')
def create_pacjent_2(id_pacjenta: int, request: PacjentCreateForm, db: Session = Depends(get_db), current_user: User = Depends(get_user_from_token("access_token"))):
    logger.info("User %s updating pacjent form for ID: %d", current_user.Username, id_pacjenta)
    return pacjent_functions.create_pacjent_form(db, id_pacjenta, request)

@router.put('/update')
def update_pacjent(id_pacjenta: int = FastapiQuery(...), request: PacjentUpdate = None, db: Session = Depends(get_db), current_user: User = Depends(get_user_from_token("access_token"))):
    logger.info("User %s updating pacjent with ID: %d", current_user.Username, id_pacjenta)
    return pacjent_functions.update_pacjent(db, id_pacjenta, request)

@router.get('/get')
def get_pacjent(id_pacjenta: int = FastapiQuery(...), db: Session = Depends(get_db), current_user: User = Depends(get_user_from_token("access_token"))):
    logger.debug("User %s retrieving pacjent with ID: %d", current_user.Username, id_pacjenta)
    return pacjent_functions.get_pacjent_by_id(db, id_pacjenta)

@router.delete('/delete')
def delete_pacjent(id_pacjenta: int = FastapiQuery(...), db: Session = Depends(get_db), current_user: User = Depends(get_user_from_token("access_token"))):
    logger.info("User %s deleting pacjent with ID: %d", current_user.Username, id_pacjenta)
    return pacjent_functions.delete_pacjent(db, id_pacjenta)

@router.get('/search', response_model=list[PacjentDisplay])
def search_pacjenci(query: str, db: Session = Depends(get_db), current_user: User = Depends(get_user_from_token("access_token"))):
    logger.debug("User %s searching pacjenci with query: %s", current_user.Username, query)
    return pacjent_functions.search_pacjenci(db, query)

@router.get('/all', response_model=Page[PacjentDisplay])
def show_pacjent_list(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_user_from_token("access_token")),
    sort_by: str = FastapiQuery(None, description="Field to sort by"),
    sort_direction: str = FastapiQuery(None, description="'asc' or 'desc'"),
    search_term: Optional[str] = FastapiQuery(None, description="Search in name, email, phone"),
    filters: Optional[List[str]] = FastapiQuery(None, description="Filters as 'field:value' pairs. If it's a date range, write second date in the same pair, after a comma")
    ):
    logger.debug("User %s retrieving pacjent list (sort_by=%s, sort_direction=%s, search_term=%s)", current_user.Username, sort_by, sort_direction, search_term)
    return pacjent_functions.get_all_pacjenci(db, sort_by, sort_direction, search_term, filters)