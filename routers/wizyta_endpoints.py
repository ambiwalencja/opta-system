from sqlalchemy.orm.session import Session
from fastapi import APIRouter, Depends #, HTTPException, status

from auth.oauth2 import get_user_from_token
from db.db_connect import get_db
# from auth.oauth2 import get_user_from_token
# from schemas.pacjent_schemas import CreatePacjentBasic, CreatePacjentForm, DisplayPacjent, UpdatePacjent
from db_models.user_data import User
from schemas.wizyta_schemas import CreateWizytaIndywidualna, DisplayWizytaIndywidualna, UpdateWizytaIndywidualna
# from schemas.grupa_schemas import CreateGrupa, DisplayGrupa
# from db_models.client_data import Pacjent
# from db_models.user_data import User
from utils import wizyta_functions


router = APIRouter(
    prefix="/wizyta",
    tags=["wizyta"],
    responses={404: {"description": "Not found"}},
)

@router.get('/get/{id_wizyty}')
def get_wizyta_indywidualna(id_wizyty: int, db: Session = Depends(get_db), current_user: User = Depends(get_user_from_token("access_token"))):
    return wizyta_functions.get_wizyta_by_id(db, id_wizyty)

@router.post('/create', response_model=DisplayWizytaIndywidualna)
def create_wizyta_indywidualna(request: CreateWizytaIndywidualna, db: Session = Depends(get_db), current_user: User = Depends(get_user_from_token("access_token"))):
    return wizyta_functions.create_wizyta(db, request)

@router.put('/update/{id_wizyty}', response_model=DisplayWizytaIndywidualna)
def update_wizyta_indywidualna(id_wizyty: int, request: UpdateWizytaIndywidualna, db: Session = Depends(get_db), current_user: User = Depends(get_user_from_token("access_token"))):
    return wizyta_functions.update_wizyta(db, id_wizyty, request)
