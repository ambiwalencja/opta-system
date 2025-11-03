from sqlalchemy.orm.session import Session
from fastapi import APIRouter, Depends, HTTPException, status
from db.db_connect import get_db
from schemas.client_schemas import (
    DisplayPacjent, DisplayWizytaIndywidualna, DisplayPacjentWithWizyta,
    DisplayGrupa
)
from schemas.user_schemas import UserSignIn, UserDisplay
# from db_models.client_data import Pacjent
from utils import client_functions, user_functions
from auth.oauth2 import get_user_from_token


router = APIRouter(
    prefix="/front",
    tags=["front"],
    responses={404: {"description": "Not found"}},
)

@router.get('/get_pacjent', response_model=DisplayPacjent) # TODO: tutaj response to display pacjent, czy może całość?
def get_pacjent_for_front(id_pacjenta: int, db: Session = Depends(get_db)):
    return client_functions.get_pacjent_by_id(db, id_pacjenta)

@router.get('/recent_pacjenci', response_model=list[DisplayPacjentWithWizyta])
def show_recent_pacjenci(limit: int = 10, db: Session = Depends(get_db), current_user: UserSignIn = Depends(get_user_from_token("access_token"))):
    return client_functions.get_recent_pacjenci(db, current_user.ID_uzytkownika, limit)

# @router.get('/recent_wizyty', response_model=list[DisplayWizytaIndywidualna])
# def show_recent_wizyty_front(limit: int = 10, db: Session = Depends(get_db)):
#     wizyty = client_functions.get_recent_wizyty(db, limit)
#     return wizyty

@router.get('/recently_created_pacjenci', response_model=list[DisplayPacjent])
def show_recently_created_pacjenci(limit: int = 10, db: Session = Depends(get_db), current_user: UserSignIn = Depends(get_user_from_token("access_token"))):
    if current_user.Role != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
            detail=f'You are not an admin')
    return client_functions.get_recently_created_pacjenci(db, limit)


@router.get('/recently_active_users', response_model=list[UserDisplay])
def show_recently_active_users(limit: int = 10, db: Session = Depends(get_db), current_user: UserSignIn = Depends(get_user_from_token("access_token"))):
    if current_user.Role != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
            detail=f'You are not an admin')
    return user_functions.get_recently_active_users(db, limit)

@router.get('/recently_added_groups', response_model=list[DisplayGrupa])
def show_recently_added_groups(limit: int = 10, db: Session = Depends(get_db), current_user: UserSignIn = Depends(get_user_from_token("access_token"))):
    if current_user.Role != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
            detail=f'You are not an admin')
    return client_functions.get_recently_added_groups(db, limit)

@router.get('/my_groups', response_model=list[DisplayGrupa])
def show_my_groups(db: Session = Depends(get_db), current_user: UserSignIn = Depends(get_user_from_token("access_token"))):
    return client_functions.get_groups_for_user(db, current_user.ID_uzytkownika)