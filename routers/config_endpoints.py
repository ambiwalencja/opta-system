from sqlalchemy.orm.session import Session
from fastapi import APIRouter, Depends, HTTPException, status
import logging
from db.db_connect import get_db
from db import define_possible_values_table
from schemas.user_schemas import UserSignIn
from auth.oauth2 import get_user_from_token

router = APIRouter(
    prefix="/config",
    tags=["config"],
    responses={404: {"description": "Not found"}},
)

logger = logging.getLogger("opta_system_logger")

@router.post('/populate_possible_values')
def populate_values(db: Session = Depends(get_db), current_user: UserSignIn = Depends(get_user_from_token("access_token"))):
    try:
        if current_user.Role != 'admin':
            logger.warning("Unauthorized populate_values attempt by user: %s", current_user.Username)
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                detail=f'You are not an admin')
        logger.info("Populating possible values by admin %s", current_user.Username)
        define_possible_values_table.populate_possible_values(db)
        logger.info("Possible values populated successfully by admin %s", current_user.Username)
        return True
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error populating possible values: %s", str(e), exc_info=True)
        raise