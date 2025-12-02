from sqlalchemy.orm.session import Session
from fastapi import APIRouter, Depends #, HTTPException, status

from db.db_connect import get_db
from auth.oauth2 import get_user_from_token
from schemas.pacjent_schemas import PacjentDisplay
from schemas.grupa_schemas import (GrupaCreate, GrupaDisplay, 
                                   GrupaUpdate, UczestnikGrupyCreate,
                                   UczestnikGrupyDisplay)
from schemas.spot_grup_schemas import SpotkanieGrupoweCreate, SpotkanieGrupoweDisplay, SpotkanieGrupoweUpdate
# from db_models.client_data import Pacjent
from db_models.user_data import User
from utils import grupa_functions, spot_grup_functions

router = APIRouter(
    prefix="/spot_grup",
    tags=["spot_grup"],
    responses={404: {"description": "Not found"}},
)

@router.get('/{id_spotkania}')
def get_spotkanie(id_spotkania: int, db: Session = Depends(get_db), current_user: User = Depends(get_user_from_token("access_token"))):
    return spot_grup_functions.get_spotkanie_by_id(db, id_spotkania)

@router.post('/create', response_model=SpotkanieGrupoweDisplay)
def create_spotkanie_grupowe(request: SpotkanieGrupoweCreate, db: Session = Depends(get_db), current_user: User = Depends(get_user_from_token("access_token"))):
    return spot_grup_functions.create_spotkanie_grupowe(db, request, current_user.ID_uzytkownika)

@router.post('/update/{id_spotkania}', response_model=SpotkanieGrupoweDisplay)
def create_spotkanie_grupowe(id_spotkania: int, request: SpotkanieGrupoweUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_user_from_token("access_token"))):
    return spot_grup_functions.update_spotkanie_grupowe(db, id_spotkania, request)

@router.delete('/delete/{id_spotkania}')
def delete_spotkanie_grupowe(id_spotkania: int, db: Session = Depends(get_db), current_user: User = Depends(get_user_from_token("access_token"))):
    return spot_grup_functions.delete_spotkanie_grupowe(db, id_spotkania)

# @router.get('/grupa/{id_grupy}', response_model=list[UczestnikGrupyDisplay])
# def show_all_spotkania_grup(id_grupy: int, db: Session = Depends(get_db), current_user: User = Depends(get_user_from_token("access_token"))):
#     return grupa_functions.show_uczestnicy_grupy(db, id_grupy)