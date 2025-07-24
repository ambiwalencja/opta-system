from sqlalchemy.orm.session import Session
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
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
# TODO: tutaj response dodany w body
def login(request: UserSignIn, response: Response, db: Session = Depends(get_db)):
    user = user_functions.get_user_by_username(db, request.username)
    if not Hash.verify(user.Password, request.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect password')
    
    access_token = create_access_token(data={'username': user.Username})
    refresh_token = create_refresh_token(data={"username": user.Username})
    
    user_functions.update_last_login(db, user)

    #TODO: to dodane - zapisywanie refresh tokenu do cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=REFRESH_TOKEN_EXPIRE_SECONDS
    )

    return {
        'access_token': access_token,
        "refresh_token": refresh_token,
        'token_type': 'bearer',
        'user_id': user.ID_uzytkownika,
        'username': user.Username,
        'role': user.Role
    }

@router.post('/login_form') # do testowania, do autoryzacji w docsach
def login_form(response: Response, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = user_functions.get_user_by_username(db, form_data.username)
    if not Hash.verify(user.Password, form_data.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect password')
    
    access_token = create_access_token(data={'username': user.Username})
    refresh_token = create_refresh_token(data={"username": user.Username})
    
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=REFRESH_TOKEN_EXPIRE_SECONDS
    )

    return {
        'access_token': access_token,
        "refresh_token": refresh_token,
        'token_type': 'bearer'
    }

# TODO: wersja refresha bez zapisywania tokenu w cookiesie
# @router.post('/refresh')
# def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
#     try:
#         payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
#         if payload.get("scope") != "refresh_token":
#             raise HTTPException(status_code=401, detail="Invalid scope")
#     except JWTError:
#         raise HTTPException(status_code=401, detail="Invalid refresh token")

#     user = user_functions.get_user_by_username(db, payload.get("username"))

#     new_access_token = create_access_token(data={"username": user.Username})
#     return {
#         "access_token": new_access_token,
#         "token_type": "bearer"
#     }

# TODO: wersja z cookie - z dekodowaniem tokenu na miejscu - potrzebny wtedy import jwt
# @router.post("/refresh")
# def refresh_token(request: Request):
#     refresh_token = request.cookies.get("refresh_token")
#     if not refresh_token:
#         raise HTTPException(status_code=401, detail="No refresh token")

#     try:
#         payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
#         if payload.get("scope") != "refresh_token":
#             raise HTTPException(status_code=401, detail="Invalid scope")
#     except JWTError:
#         raise HTTPException(status_code=401, detail="Invalid refresh token")

#     new_access_token = create_access_token({"username": payload.get("username")})
#     return {"access_token": new_access_token}

# wersja z cookie - z dekodowaniem tokenu w osobnej funkcji w oauth2
@router.post("/refresh2")
def refresh_token2(request: Request, db: Session = Depends(get_db)):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No refresh token")

    user = get_user_from_token_raw(refresh_token, "refresh_token", db)

    new_access_token = create_access_token({"username": user.Username})
    return {"access_token": new_access_token}


# ver 1 - z użyciem get_current_user
@router.get('/me', response_model=UserDisplay)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user


# ver 2 - z użyciem get_user_from_token (dla access i refresh tokena)
@router.get("/me", response_model=UserDisplay)
def get_me(current_user: User = Depends(get_user_from_token("access_token"))):
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

#TODO: czat zaproponował też taki endpoint:
@router.post('/logout')
def logout(response: Response):
    response.delete_cookie("refresh_token")
    return {"message": "Logged out"}