from sqlalchemy.orm.session import Session
from fastapi import APIRouter, Depends, HTTPException, status
from db.db_connect import get_db
from schemas.client_schemas import DisplayPacjent, DisplayWizytaIndywidualna, DisplayPacjentWithWizyta
from schemas.user_schemas import UserSignIn
from db_models.client_data import Pacjent
from utils import client_functions
from auth.oauth2 import get_user_from_token


router = APIRouter(
    prefix="/front",
    tags=["front"],
    responses={404: {"description": "Not found"}},
)

@router.get('/recent_pacjenci', response_model=list[DisplayPacjentWithWizyta])
def show_recent_pacjenci_front(limit: int = 10, db: Session = Depends(get_db), current_user: UserSignIn = Depends(get_user_from_token("access_token"))):
    return client_functions.get_recent_pacjenci(db, current_user.ID_uzytkownika, limit)

@router.get('/recent_wizyty', response_model=list[DisplayWizytaIndywidualna])
def show_recent_wizyty_front(limit: int = 10, db: Session = Depends(get_db)):
    wizyty = client_functions.get_recent_wizyty(db, limit)
    return wizyty

@router.get('/get_pacjent', response_model=DisplayPacjent)
def get_pacjent_for_front(id_pacjenta: int, db: Session = Depends(get_db)):
    pacjent = db.query(Pacjent).filter(Pacjent.ID_pacjenta == id_pacjenta).first()
    if not pacjent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Pacjent with ID {id_pacjenta} not found")
    return pacjent
