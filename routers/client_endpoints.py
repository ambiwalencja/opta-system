from sqlalchemy.orm.session import Session
from fastapi import APIRouter, Depends, HTTPException, status
from db.db_connect import get_db
from schemas.client_schemas import CreatePacjent, DisplayPacjent
from db_models.client_data import Pacjent
from utils import client_functions


router = APIRouter(
    prefix="/client",
    tags=["client"],
    responses={404: {"description": "Not found"}},
)

@router.post('/create', response_model=DisplayPacjent) # passphrase?
def create_pacjent(request: CreatePacjent, passphrase: str, db: Session = Depends(get_db)):
    # # check passphrase - ??? # TODO: passphrase tutaj też?
    # if passphrase != os.environ.get('REGISTER_PASSPHRASE'):
    #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
    #         detail='Incorrect passphrase')


    # check for duplicates - phone, email, fullname+address
    if db.query(Pacjent).filter(Pacjent.Telefon == request.telefon).first(): # TODO: i jeszcze ujednolicenie formatu telefonu!
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Client with phone number {request.telefon} already exists')
    if db.query(Pacjent).filter(Pacjent.Email == request.email).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Client with email {request.email} already exists')
    if (db.query(Pacjent).filter(Pacjent.Imie == request.imie).first() and
        db.query(Pacjent).filter(Pacjent.Nazwisko == request.nazwisko).first() and
        db.query(Pacjent).filter(Pacjent.Dzielnica == request.dzielnica).first() and
        db.query(Pacjent).filter(Pacjent.Nr_domu == request.nr_domu).first()):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Client with email {request.email} already exists')
    
    # 2. Dynamic validation of all choice fields
    data_dict = request.model_dump(by_alias=True, exclude_unset=True)

    # for field_name, field_value in data_dict.items():
    #     if field_value is not None:  
    #         client_functions.validate_choice(db, field_name, field_value)
    
    for field_name, field_value in data_dict.items():
        if field_value is not None:
            # Check for list fields (korzystanie z pomocy, problemy, zaproponowane wsparcie)
            if isinstance(field_value, list):
                for item in field_value:
                    client_functions.validate_choice(db, field_name, item)
            else:
                client_functions.validate_choice(db, field_name, field_value)

    return client_functions.create_pacjent(db, request)

@router.post('/update', response_model=DisplayPacjent)
def update_pacjent():
    pass

