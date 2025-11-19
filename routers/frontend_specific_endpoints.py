from sqlalchemy.orm.session import Session
from fastapi import APIRouter, Depends, HTTPException, status

from auth.oauth2 import get_user_from_token
from db.db_connect import get_db
# from db_models.client_data import Pacjent
from schemas.pacjent_schemas import PacjentDisplay, PacjentWithWizytaDisplay
# from schemas.wizyta_schemas import WizytaIndywidualnaDisplay
from schemas.grupa_schemas import GrupaDisplay
from schemas.user_schemas import UserSignIn, UserDisplay
from utils import pacjent_functions, user_functions, grupa_functions


router = APIRouter(
    prefix="/front",
    tags=["front"],
    responses={404: {"description": "Not found"}},
)

@router.get('/recent_pacjenci', response_model=list[PacjentWithWizytaDisplay])
def show_recent_pacjenci(limit: int = 10, db: Session = Depends(get_db), current_user: UserSignIn = Depends(get_user_from_token("access_token"))):
    return pacjent_functions.get_recent_pacjenci(db, current_user.ID_uzytkownika, limit)

# @router.get('/recent_wizyty', response_model=list[WizytaIndywidualnaDisplay])
# def show_recent_wizyty_front(limit: int = 10, db: Session = Depends(get_db)):
#     wizyty = wizyty_functions.get_recent_wizyty(db, limit)
#     return wizyty

@router.get('/recently_created_pacjenci', response_model=list[PacjentDisplay])
def show_recently_created_pacjenci(limit: int = 10, db: Session = Depends(get_db), current_user: UserSignIn = Depends(get_user_from_token("access_token"))):
    if current_user.Role != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
            detail=f'You are not an admin')
    return pacjent_functions.get_recently_created_pacjenci(db, limit)

@router.get('/recently_active_users', response_model=list[UserDisplay])
def show_recently_active_users(limit: int = 10, db: Session = Depends(get_db), current_user: UserSignIn = Depends(get_user_from_token("access_token"))):
    if current_user.Role != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
            detail=f'You are not an admin')
    return user_functions.get_recently_active_users(db, limit)

@router.get('/recently_added_groups', response_model=list[GrupaDisplay])
def show_recently_added_groups(limit: int = 10, db: Session = Depends(get_db), current_user: UserSignIn = Depends(get_user_from_token("access_token"))):
    if current_user.Role != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
            detail=f'You are not an admin')
    return grupa_functions.get_recently_added_groups(db, limit)

@router.get('/my_groups', response_model=list[GrupaDisplay])
def show_my_groups(db: Session = Depends(get_db), current_user: UserSignIn = Depends(get_user_from_token("access_token"))):
    return grupa_functions.get_groups_for_user(db, current_user.ID_uzytkownika)

@router.get('/my_current_groups', response_model=list[GrupaDisplay])
def show_my_current_groups(db: Session = Depends(get_db), current_user: UserSignIn = Depends(get_user_from_token("access_token"))):
    return grupa_functions.get_current_groups_for_user(db, current_user.ID_uzytkownika)
