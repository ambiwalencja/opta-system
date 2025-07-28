from sqlalchemy.orm.session import Session
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
import os
from db.db_connect import get_db
from schemas.user_schemas import UserBase, UserDisplay, UserSignIn
from db_models.user_data import User
from utils import user_functions
from auth.hashing import Hash
from auth.oauth2 import create_access_token, create_refresh_token, get_current_user
from auth.oauth2 import get_user_from_token_raw, get_user_from_token

REFRESH_TOKEN_EXPIRE_DAYS = int(os.environ.get('REFRESH_TOKEN_EXPIRE_DAYS'))
REFRESH_TOKEN_EXPIRE_SECONDS = REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60

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
    refresh_token = create_refresh_token(data={"username": user.Username})
    
    user_functions.update_last_login(db, user)

    return {
        'access_token': access_token,
        "refresh_token": refresh_token,
        'token_type': 'bearer',
        'user_id': user.ID_uzytkownika,
        'username': user.Username,
        'role': user.Role
    }

@router.post('/login_form') # do testowania, do autoryzacji w docsach
def login_form(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = user_functions.get_user_by_username(db, form_data.username)
    if not Hash.verify(user.Password, form_data.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect password')
    
    access_token = create_access_token(data={'username': user.Username})
    refresh_token = create_refresh_token(data={"username": user.Username})
    
    return {
        'access_token': access_token,
        "refresh_token": refresh_token,
        'token_type': 'bearer'
    }


@router.post("/refresh")
async def refresh_token(request: Request, db: Session = Depends(get_db)):
    body = await request.json()
    refresh_token = body.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No refresh token")

    user = get_user_from_token_raw(refresh_token, "refresh_token", db)

    new_access_token = create_access_token({"username": user.Username})
    return {"access_token": new_access_token}


# # ver 1 - z użyciem get_current_user
# @router.get('/me', response_model=UserDisplay)
# def get_current_user_info(current_user: User = Depends(get_current_user)):
#     return current_user


# ver 2 - z użyciem get_user_from_token (dla access i refresh tokena)
@router.get("/me", response_model=UserDisplay)
def get_me(current_user: User = Depends(get_user_from_token("access_token"))):
    return current_user


@router.post('/reset')
def reset_password_for_user(request: UserSignIn, db: Session = Depends(get_db), current_user: UserSignIn = Depends(get_user_from_token("access_token"))):
# def reset_password_for_user(request: UserSignIn, db: Session = Depends(get_db), current_user: UserSignIn = Depends(get_current_user)):
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

@router.post('/display')
def display_users(db: Session = Depends(get_db), current_user: UserSignIn = Depends(get_user_from_token("access_token"))):
    data = db.query(User.ID_uzytkownika, User.Username, User.Role, User.Last_login).all() # z bazy wyciągamy tylko wybrane kolumny, bez hasła
    response_data = []
    for row in data:
        response_data.append({
            'ID': row[0],
            'Username': row[1],
            'Role': row[2],
            'Last login': row[3]
        })
    return response_data

@router.post('/delete')
def delete_users(term: str, db: Session = Depends(get_db), current_user: UserSignIn = Depends(get_user_from_token("access_token"))): 
    if current_user.Role != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
            detail=f'You are not an admin')
    user = db.query(User).filter(User.Username == term).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
            detail=f'User {term} does not exist')
    db.delete(user)
    db.commit()
    return True