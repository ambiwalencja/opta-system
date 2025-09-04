from sqlalchemy.orm.session import Session
from fastapi import APIRouter, Depends, HTTPException, status
from db.db_connect import get_db
from db import define_possible_values_table
from schemas.user_schemas import UserSignIn
from auth.oauth2 import get_user_from_token

router = APIRouter(
    prefix="/config",
    tags=["config"],
    responses={404: {"description": "Not found"}},
)

@router.post('/populate_possible_values')
def populate_values(db: Session = Depends(get_db), current_user: UserSignIn = Depends(get_user_from_token("access_token"))):
    if current_user.Role != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
            detail=f'You are not an admin')
    define_possible_values_table.populate_possible_values(db)
    
    return True