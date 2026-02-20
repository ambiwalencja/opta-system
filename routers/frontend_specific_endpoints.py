from sqlalchemy.orm.session import Session
from fastapi import APIRouter, Depends, HTTPException, status, Query as FastapiQuery
import logging
from typing import Optional

from auth.oauth2 import get_user_from_token
from db.db_connect import get_db
# from db_models.client_data import Pacjent
from schemas.pacjent_schemas import PacjentDisplay, PacjentWithWizytaDisplay
from schemas.wizyta_schemas import WizytaIndywidualnaDisplay, WizytaIndywidualnaUpdate
from schemas.grupa_schemas import GrupaDisplay
from schemas.user_schemas import UserSignIn, UserDisplay
from utils import pacjent_functions, user_functions, grupa_functions, wizyta_functions


router = APIRouter(
    prefix="/front",
    tags=["front"],
    responses={404: {"description": "Not found"}},
)

logger = logging.getLogger("opta_system_logger")

@router.get('/recent_pacjenci', response_model=list[PacjentWithWizytaDisplay])
def show_recent_pacjenci(limit: int = 10, db: Session = Depends(get_db), current_user: UserSignIn = Depends(get_user_from_token("access_token"))):
    logger.info("User %s viewing recent pacjenci", current_user.Username)
    return pacjent_functions.get_recent_pacjenci(db, current_user.ID_uzytkownika, limit)

@router.get('/recently_created_pacjenci', response_model=list[PacjentDisplay])
def show_recently_created_pacjenci(limit: int = 10, db: Session = Depends(get_db), current_user: UserSignIn = Depends(get_user_from_token("access_token"))):
    if current_user.Role != 'admin':
        logger.warning("Unauthorized recently_created_pacjenci request by user: %s", current_user.Username)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
            detail=f'You are not an admin')
    logger.info("User %s (admin) viewing recently created pacjenci", current_user.Username)
    return pacjent_functions.get_recently_created_pacjenci(db, limit)

@router.get('/recently_active_users', response_model=list[UserDisplay])
def show_recently_active_users(limit: int = 10, db: Session = Depends(get_db), current_user: UserSignIn = Depends(get_user_from_token("access_token"))):
    try:
        if current_user.Role != 'admin':
            logger.warning("Unauthorized recently_active_users request by user: %s", current_user.Username)
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                detail=f'You are not an admin')
        logger.info("User %s (admin) viewing recently active users", current_user.Username)
        return user_functions.get_recently_active_users(db, limit)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error retrieving recently active users: %s", str(e), exc_info=True)
        raise

@router.get('/recently_added_groups', response_model=list[GrupaDisplay])
def show_recently_added_groups(limit: int = 10, db: Session = Depends(get_db), 
                               current_user: UserSignIn = Depends(get_user_from_token("access_token"))):
    try:
        if current_user.Role != 'admin':
            logger.warning("Unauthorized recently_added_groups request by user: %s", current_user.Username)
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                detail=f'You are not an admin')
        logger.info("User %s (admin) viewing recently added groups", current_user.Username)
        return grupa_functions.get_recently_added_groups(db, limit)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error retrieving recently added groups: %s", str(e), exc_info=True)
        raise

@router.get('/my_groups', response_model=list[GrupaDisplay])
def show_my_groups(db: Session = Depends(get_db), 
                   current_user: UserSignIn = Depends(get_user_from_token("access_token"))):
    logger.info("User %s viewing their groups", current_user.Username)
    return grupa_functions.get_groups_for_user(db, current_user.ID_uzytkownika)

@router.get('/my_current_groups', response_model=list[GrupaDisplay])
def show_my_current_groups(db: Session = Depends(get_db), 
                           current_user: UserSignIn = Depends(get_user_from_token("access_token"))):
    logger.info("User %s viewing their current groups", current_user.Username)
    return grupa_functions.get_current_groups_for_user(db, current_user.ID_uzytkownika)

@router.get('/my_recent_wizyty', response_model=list[WizytaIndywidualnaDisplay])
def show_my_recent_wizyty(limit: Optional[int] = FastapiQuery(10, description="Optional limit for recent wizyty"), 
                          db: Session = Depends(get_db), 
                          current_user: UserSignIn = Depends(get_user_from_token("access_token"))):
    '''Show wizyty for the current user, with default limit 10'''
    logger.info("User %s viewing their recent wizyty with limit: %d", current_user.Username, limit)
    wizyty = wizyta_functions.get_recent_wizyty_for_user(db, current_user.ID_uzytkownika, limit)
    return wizyty

@router.get('/recent_wizyty_for_pacjent', response_model=list[WizytaIndywidualnaDisplay]    )
def show_recent_wizyty_for_pacjent(id_pacjenta: Optional[int] = FastapiQuery(None, description="ID of the pacjent to show wizyty for"), 
                                   limit: Optional[int] = FastapiQuery(None, description="Optional limit for recent wizyty"),
                                   db: Session = Depends(get_db), 
                                   current_user: UserSignIn = Depends(get_user_from_token("access_token"))):
    '''Show recent wizyty for the pacjent, with optional limit'''
    logger.info("User %s viewing recent wizyty for pacjent with ID: %d and limit: %d", current_user.Username, id_pacjenta, limit)
    wizyty = wizyta_functions.get_recent_wizyty_for_pacjent(db, id_pacjenta, limit)
    return wizyty

@router.get('/detailed_wizyty_for_pacjent', response_model=list[WizytaIndywidualnaUpdate]    )
def show_recent_detailed_wizyty_for_pacjent(id_pacjenta: Optional[int] = FastapiQuery(None, description="ID of the pacjent to show wizyty for"), 
                                   limit: Optional[int] = FastapiQuery(None, description="Optional limit for recent wizyty"),
                                   db: Session = Depends(get_db), 
                                   current_user: UserSignIn = Depends(get_user_from_token("access_token"))):
    '''Show recent wizyty for the pacjent, with optional limit'''
    logger.info("User %s viewing recent wizyty for pacjent with ID: %d and limit: %d", current_user.Username, id_pacjenta, limit)
    wizyty = wizyta_functions.get_recent_wizyty_for_pacjent(db, id_pacjenta, limit)
    return wizyty