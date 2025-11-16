from sqlalchemy.orm.session import Session
from fastapi import APIRouter, Depends #, HTTPException, status

from db.db_connect import get_db
from auth.oauth2 import get_user_from_token
# from schemas.pacjent_schemas import CreatePacjentBasic, CreatePacjentForm, DisplayPacjent, UpdatePacjent
# from schemas.wizyta_schemas import CreateWizytaIndywidualna, DisplayWizytaIndywidualna
from schemas.grupa_schemas import CreateGrupa, DisplayGrupa, UpdateGrupa
# from db_models.client_data import Pacjent
from db_models.user_data import User
from utils import grupa_functions


router = APIRouter(
    prefix="/grupa",
    tags=["grupa"],
    responses={404: {"description": "Not found"}},
)

@router.get('/{id_grupy}')
def get_grupa(id_grupy: int, db: Session = Depends(get_db), current_user: User = Depends(get_user_from_token("access_token"))):
    return grupa_functions.get_grupa_by_id(db, id_grupy)

@router.post('/create', response_model=DisplayGrupa)
def create_grupa(request: CreateGrupa, db: Session = Depends(get_db), current_user: User = Depends(get_user_from_token("access_token"))):
    return grupa_functions.create_grupa(db, request, current_user.ID_uzytkownika)

@router.put('/update/{id_grupy}', response_model=DisplayGrupa)
def update_grupa(id_grupy: int, request: UpdateGrupa, db: Session = Depends(get_db), current_user: User = Depends(get_user_from_token("access_token"))):
    return grupa_functions.update_grupa(db, id_grupy, request, current_user.ID_uzytkownika)