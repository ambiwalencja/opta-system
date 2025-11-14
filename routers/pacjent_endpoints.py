from sqlalchemy.orm.session import Session
from fastapi import APIRouter, Depends, HTTPException, status

from db.db_connect import get_db
from auth.oauth2 import get_user_from_token
from schemas.pacjent_schemas import CreatePacjentBasic, CreatePacjentForm, DisplayPacjent, UpdatePacjent
# from schemas.wizyta_schemas import CreateWizytaIndywidualna, DisplayWizytaIndywidualna
# from schemas.grupa_schemas import CreateGrupa, DisplayGrupa
# from db_models.client_data import Pacjent
from db_models.user_data import User
from utils import pacjent_functions


router = APIRouter(
    prefix="/pacjent",
    tags=["pacjent"],
    responses={404: {"description": "Not found"}},
)

@router.post('/create_basic', response_model=DisplayPacjent) # passphrase?
def create_pacjent_1(request: CreatePacjentBasic, db: Session = Depends(get_db), current_user: User = Depends(get_user_from_token("access_token"))):
    return pacjent_functions.create_pacjent_basic(db, request, current_user.ID_uzytkownika)

@router.post('/create_form')
def create_pacjent_2(id_pacjenta: int, request: CreatePacjentForm, db: Session = Depends(get_db), current_user: User = Depends(get_user_from_token("access_token"))):
    return pacjent_functions.create_pacjent_form(db, id_pacjenta, request)

@router.post('/update') # jesli to ma być wykorzystane do merge to musi zwracać całego pacjenta
def update_pacjent(id_pacjenta: int, request: UpdatePacjent, db: Session = Depends(get_db), current_user: User = Depends(get_user_from_token("access_token"))):
    return pacjent_functions.update_pacjent(db, id_pacjenta, request)

@router.get('/get') # musi zwracać całego pacjenta
def get_pacjent(id_pacjenta: int, db: Session = Depends(get_db), current_user: User = Depends(get_user_from_token("access_token"))):
    return pacjent_functions.get_pacjent_by_id(db, id_pacjenta)



