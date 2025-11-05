from sqlalchemy.orm.session import Session
from fastapi import APIRouter, Depends #, HTTPException, status

from db.db_connect import get_db
# from auth.oauth2 import get_user_from_token
# from schemas.pacjent_schemas import CreatePacjentBasic, CreatePacjentForm, DisplayPacjent, UpdatePacjent
from schemas.wizyta_schemas import CreateWizytaIndywidualna, DisplayWizytaIndywidualna
# from schemas.grupa_schemas import CreateGrupa, DisplayGrupa
# from db_models.client_data import Pacjent
# from db_models.user_data import User
from utils import wizyta_functions


router = APIRouter(
    prefix="/wizyta",
    tags=["wizyta"],
    responses={404: {"description": "Not found"}},
)

@router.post('/create', response_model=DisplayWizytaIndywidualna)
def create_wizyta_indywidualna(request: CreateWizytaIndywidualna, db: Session = Depends(get_db)):
    return wizyta_functions.create_wizyta(db, request)