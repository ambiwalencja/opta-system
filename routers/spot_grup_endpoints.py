from sqlalchemy.orm.session import Session
from fastapi import APIRouter, Depends, Query as FastapiQuery, HTTPException, status
import logging

from db.db_connect import get_db
from auth.oauth2 import get_user_from_token
from schemas.spot_grup_schemas import SpotkanieGrupoweCreate, SpotkanieGrupoweDisplay, SpotkanieGrupoweUpdate
from db_models.user_data import User
from utils import spot_grup_functions

logger = logging.getLogger("opta_system_logger")

router = APIRouter(
    prefix="/spot_grup",
    tags=["spot_grup"],
    responses={404: {"description": "Not found"}},
)

@router.get('/')
def get_spotkanie(id_spotkania: int = FastapiQuery(...), db: Session = Depends(get_db), current_user: User = Depends(get_user_from_token("access_token"))):
    logger.debug("User %s retrieving spotkanie grupowe with ID: %d", current_user.Username, id_spotkania)
    return spot_grup_functions.get_spotkanie_by_id(db, id_spotkania)

@router.post('/create', response_model=SpotkanieGrupoweDisplay)
def create_spotkanie_grupowe(request: SpotkanieGrupoweCreate, db: Session = Depends(get_db), current_user: User = Depends(get_user_from_token("access_token"))):
    logger.info("User %s creating new spotkanie grupowe", current_user.Username)
    return spot_grup_functions.create_spotkanie_grupowe(db, request, current_user.ID_uzytkownika)

@router.post('/update/', response_model=SpotkanieGrupoweDisplay)
def update_spotkanie_grupowe(request: SpotkanieGrupoweUpdate, id_spotkania: int = FastapiQuery(...),  db: Session = Depends(get_db), current_user: User = Depends(get_user_from_token("access_token"))):
    logger.info("User %s updating spotkanie grupowe with ID: %d", current_user.Username, id_spotkania)
    return spot_grup_functions.update_spotkanie_grupowe(db, id_spotkania, request)

@router.delete('/delete/')
def delete_spotkanie_grupowe(id_spotkania: int = FastapiQuery(...), db: Session = Depends(get_db), current_user: User = Depends(get_user_from_token("access_token"))):
    logger.info("User %s deleting spotkanie grupowe with ID: %d", current_user.Username, id_spotkania)
    return spot_grup_functions.delete_spotkanie_grupowe(db, id_spotkania)

# @router.get('/grupa/', response_model=list[UczestnikGrupyDisplay])
# def show_all_spotkania_grup(id_grupy: int = FastapiQuery(...), db: Session = Depends(get_db), current_user: User = Depends(get_user_from_token("access_token"))):
#     return grupa_functions.show_uczestnicy_grupy(db, id_grupy)