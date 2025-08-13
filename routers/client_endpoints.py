from sqlalchemy.orm.session import Session
from fastapi import APIRouter, Depends, HTTPException, status
import os
from db.db_connect import get_db
from schemas.client_schemas import ClientCreate, ClientDisplay
from db_models.client_data import Pacjent
from utils import client_functions


# TODO: aaaaaaa mamy angielski i polski aaaaa client i pacjent 
router = APIRouter(
    prefix="/client",
    tags=["client"],
    responses={404: {"description": "Not found"}},
)

@router.post('/create', response_model=ClientDisplay) # passphrase?
def create_client(request: ClientCreate, passphrase: str, db: Session = Depends(get_db)):
    # # check passphrase - ??? # TODO: passphrase tutaj też?
    # if passphrase != os.environ.get('REGISTER_PASSPHRASE'):
    #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
    #         detail='Incorrect passphrase')
    # check for duplicates - phone - TODO: uzupełnić sprawdzanie duplikatów
    if db.query(Pacjent).filter(Pacjent.Telefon == request.telefon).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
            detail='Client already exists')
    
    return client_functions.create_client(db, request)

@router.post('/update', response_model=ClientDisplay)
def update_client():
    pass

