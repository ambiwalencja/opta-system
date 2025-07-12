from sqlalchemy.orm.session import Session
from fastapi import APIRouter, Depends, HTTPException, status
import os
from db.db_connect import get_db
from schemas.user_schemas import UserBase, UserDisplay
from db_models.user_data import User
# from auth.hashing import Hash
from utils import user_functions


router = APIRouter(
    prefix="/user",
    tags=["user"],
    responses={404: {"description": "Not found"}},
)


@router.post('/create/{passphrase}', response_model=UserDisplay)
def create_user(request: UserBase, passphrase: str, db: Session = Depends(get_db)):
    # check passphrase
    if passphrase != os.environ.get('REGISTER_PASSPHRASE'):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
            detail='Incorrect passphrase')
    # check if user already exists
    if db.query(User).filter(User.Username == request.username).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
            detail='User already exists')
    return user_functions.create_user(db, request)


