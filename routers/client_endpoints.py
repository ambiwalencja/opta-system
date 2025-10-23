from sqlalchemy.orm.session import Session
from fastapi import APIRouter, Depends, HTTPException, status
from db.db_connect import get_db
from schemas.client_schemas import (
    CreatePacjentBasic, CreatePacjentForm, DisplayPacjent, UpdatePacjent,
    CreateWizytaIndywidualna, DisplayWizytaIndywidualna
)
from db_models.client_data import Pacjent
from utils import client_functions

from db_models.user_data import User
from auth.oauth2 import get_user_from_token

router = APIRouter(
    prefix="/client",
    tags=["client"],
    responses={404: {"description": "Not found"}},
)

@router.post('/create_basic', response_model=DisplayPacjent) # passphrase?
def create_pacjent_1(request: CreatePacjentBasic, db: Session = Depends(get_db), current_user: User = Depends(get_user_from_token("access_token"))):
    return client_functions.create_pacjent_basic(db, request, current_user.ID_uzytkownika)

@router.post('/create_form')
def create_pacjent_2(id_pacjenta: int, request: CreatePacjentForm, db: Session = Depends(get_db)):
    return client_functions.create_pacjent_form(db, id_pacjenta, request)

@router.post('/update') # jesli to ma być wykorzystane do merge to musi zwracać całego pacjenta
def update_pacjent(id_pacjenta: int, request: UpdatePacjent, db: Session = Depends(get_db)):
    return client_functions.update_pacjent(db, id_pacjenta, request)

@router.post('/get') # tez musi zwracać całego pacjenta
def get_pacjent_for_merge(id_pacjenta: int, db: Session = Depends(get_db)):
    pacjent = db.query(Pacjent).filter(Pacjent.ID_pacjenta == id_pacjenta).first()
    return pacjent

@router.post('/visit/create', response_model=DisplayWizytaIndywidualna) # passphrase?
def create_wizyta_indywidualna(request: CreateWizytaIndywidualna, db: Session = Depends(get_db)):
    return client_functions.create_wizyta(db, request)

