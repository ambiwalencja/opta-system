from sqlalchemy.orm.session import Session
from fastapi import APIRouter, Depends #, HTTPException, status

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

@router.get('/{id_grupy}', response_model=GrupaDisplay)
def get_grupa(id_grupy: int, db: Session = Depends(get_db), current_user: User = Depends(get_user_from_token("access_token"))):
    return grupa_functions.get_grupa_by_id(db, id_grupy)

@router.post('/create', response_model=GrupaDisplay)
def create_grupa(request: GrupaCreate, db: Session = Depends(get_db), current_user: User = Depends(get_user_from_token("access_token"))):
    return grupa_functions.create_grupa(db, request, current_user.ID_uzytkownika)

@router.put('/update/{id_grupy}', response_model=GrupaDisplay)
def update_grupa(id_grupy: int, request: GrupaUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_user_from_token("access_token"))):
    return grupa_functions.update_grupa(db, id_grupy, request, current_user.ID_uzytkownika)

@router.delete('/delete/{id_grupy}')
def delete_grupa(id_grupy: int, db: Session = Depends(get_db), current_user: User = Depends(get_user_from_token("access_token"))):
    return grupa_functions.delete_grupa(db, id_grupy)

@router.post('/uczestnik/create', response_model=UczestnikGrupyDisplay)
def create_uczestnik_grupy(request: UczestnikGrupyCreate, db: Session = Depends(get_db), current_user: User = Depends(get_user_from_token("access_token"))):
    return grupa_functions.create_uczestnik_grupy(db, request)

@router.get('/uczestnik/{id_uczestnika_grupy}', response_model=UczestnikGrupyDisplay)
def get_uczestnik_grupy(id_uczestnika_grupy: int, db: Session = Depends(get_db), current_user: User = Depends(get_user_from_token("access_token"))):
    return grupa_functions.get_uczestnik_grupy_by_id(db, id_uczestnika_grupy)

@router.put('/uczestnik/update/{id_uczestnika_grupy}', response_model=UczestnikGrupyDisplay)
def update_uczestnik_grupy(id_uczestnika_grupy: int, request: UczestnikGrupyUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_user_from_token("access_token"))):
    return grupa_functions.update_uczestnik_grupy(db, id_uczestnika_grupy, request)

@router.delete('/uczestnik/delete/{id_uczestnika_grupy}')
def delete_uczestnik_grupy(id_uczestnika_grupy: int, db: Session = Depends(get_db), current_user: User = Depends(get_user_from_token("access_token"))):
    return grupa_functions.delete_uczestnik_grupy(db, id_uczestnika_grupy)

@router.get('/uczestnicy/{id_grupy}', response_model=list[UczestnikGrupyDisplay])
def show_uczestnicy_grupy(id_grupy: int, db: Session = Depends(get_db), current_user: User = Depends(get_user_from_token("access_token"))):
    return grupa_functions.show_uczestnicy_grupy(db, id_grupy)