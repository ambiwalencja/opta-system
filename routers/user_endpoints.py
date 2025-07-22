from sqlalchemy.orm.session import Session
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
import os
from db.db_connect import get_db
from schemas.user_schemas import UserBase, UserDisplay, UserSignIn
from db_models.user_data import User
from utils import user_functions
from auth.hashing import Hash
from auth.oauth2 import create_access_token, get_current_user


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


@router.post('/login')
def login(request: UserSignIn, db: Session = Depends(get_db)):
    user = user_functions.get_user_by_username(db, request.username)
    if not Hash.verify(user.Password, request.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect password')
    
    access_token = create_access_token(data={'username': user.Username})
    
    user_functions.update_last_login(db, user)

    return {
        'access_token': access_token,
        'token_type': 'bearer',
        'user_id': user.ID_uzytkownika,
        'username': user.Username,
        'role': user.Role
    }

@router.post('/login_form')
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)): # mogą sie tak samo nazywać dwa endpointy?
    user = user_functions.get_user_by_username(db, form_data.username)
    if not Hash.verify(user.Password, form_data.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect password')
    
    access_token = create_access_token(data={'username': user.Username})

    return {
        'access_token': access_token,
        'token_type': 'bearer'
    }


@router.get('/me', response_model=UserDisplay) # 
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user


@router.post('/reset')
def reset_password_for_user(request: UserSignIn, db: Session = Depends(get_db), current_user: UserSignIn = Depends(get_current_user)):
    user = db.query(User).filter(User.Username == request.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
            detail=f'User {request.username} does not exist')
    if current_user.Role != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
            detail=f'You are not an admin')
    user.Password = Hash.bcrypt(request.password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return True