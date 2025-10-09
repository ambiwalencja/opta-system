from sqlalchemy.orm.session import Session
from fastapi import APIRouter, Depends, HTTPException, status
from db.db_connect import get_db
from schemas.client_schemas import CreatePacjent, DisplayPacjent, CreateWizytaIndywidualna, DisplayWizytaIndywidualna
from db_models.client_data import Pacjent
from utils import client_functions


router = APIRouter(
    prefix="/client",
    tags=["client"],
    responses={404: {"description": "Not found"}},
)

@router.post('/create', response_model=DisplayPacjent) # passphrase?
def create_pacjent(request: CreatePacjent, db: Session = Depends(get_db)):
    return client_functions.create_pacjent(db, request)

@router.post('/update', response_model=DisplayPacjent)
def update_pacjent():
    pass

@router.post('/merge', response_model=DisplayPacjent) # passphrase?
def create_pacjent(request: CreatePacjent, db: Session = Depends(get_db)):
    return client_functions.create_pacjent(db, request)

@router.post('/visit/create', response_model=DisplayWizytaIndywidualna) # passphrase?
def create_wizyta_indywidualna(request: CreateWizytaIndywidualna, db: Session = Depends(get_db)):
    return client_functions.create_wizyta(db, request)

