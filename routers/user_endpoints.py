from sqlalchemy.orm.session import Session
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
import os
from db.db_connect import get_db
from schemas.user_schemas import UserCreate, UserDisplay, UserSignIn, TokenRequest, RoleEnum, StatusEnum, UserUpdate
from db_models.user_data import User
from db_models.config import PossibleValues
from utils import user_functions
from auth.hashing import Hash
from auth.oauth2 import create_access_token, create_refresh_token #, get_current_user
from auth.oauth2 import get_user_from_token_raw, get_user_from_token
# from typing import Optional
from io import BytesIO
from fastapi import UploadFile, File
from old_db.data_import import import_users_from_csv_simple
from utils.validation import validate_specialist_types



REFRESH_TOKEN_EXPIRE_DAYS = int(os.environ.get('REFRESH_TOKEN_EXPIRE_DAYS'))
REFRESH_TOKEN_EXPIRE_SECONDS = REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60

router = APIRouter(
    prefix="/user",
    tags=["user"],
    responses={404: {"description": "Not found"}},
)

@router.post('/create/{passphrase}', response_model=UserDisplay)
async def create_user(request: UserCreate, passphrase: str, db: Session = Depends(get_db)):
    # check passphrase
    if passphrase != os.environ.get('REGISTER_PASSPHRASE'):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
            detail='Incorrect passphrase')
    # validate request
    await validate_specialist_types(db, request.specjalista)
    # check if user already exists
    if db.query(User).filter(User.Username == request.username).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
            detail='User already exists')
    return await user_functions.create_user(db, request)

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
        'full_name': user.Full_name,
        'role': user.Role
    }
# TODO: kiedy używać response model, a kiedy takiego returna w diccie?

@router.post('/login_form') # do testowania, do autoryzacji w docsach
def login_form(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = user_functions.get_user_by_username(db, form_data.username)
    if not Hash.verify(user.Password, form_data.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect password')
    
    access_token = create_access_token(data={'username': user.Username})
    refresh_token = create_refresh_token(data={"username": user.Username})
    
    return {
        'full_name': user.Full_name,
        'access_token': access_token,
        "refresh_token": refresh_token,
        'token_type': 'bearer'
    }


@router.post("/refresh")
async def refresh_token(data: TokenRequest, db: Session = Depends(get_db)):
    refresh_token = data.refresh_token
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No refresh token")

    user = get_user_from_token_raw(refresh_token, "refresh_token", db)

    new_access_token = create_access_token({"username": user.Username})
    return {"access_token": new_access_token}

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

@router.get('/display')
def display_users(db: Session = Depends(get_db), current_user: UserSignIn = Depends(get_user_from_token("access_token"))):
    if current_user.Role != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
            detail=f'You are not an admin')
    data = db.query(User.ID_uzytkownika, 
                    User.Username, 
                    User.Full_name, 
                    User.Specjalista, 
                    User.Role, 
                    User.Created, 
                    User.Last_login, 
                    User.Status).all()
    response_data = []
    for row in data:
        response_data.append({
            'ID': row[0],
            'Username': row[1],
            'Full name': row[2],
            'Specjalista': row[3],
            'Role': row[4],
            'Created': user_functions.format_datetime(row[5]),
            'Last login': user_functions.format_datetime(row[6]),
            'Status': row[7]
        })
    return response_data

@router.post('/delete')
def delete_users(username: str, db: Session = Depends(get_db), current_user: UserSignIn = Depends(get_user_from_token("access_token"))): 
    if current_user.Role != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
            detail=f'You are not an admin')
    user = db.query(User).filter(User.Username == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
            detail=f'User with username {username} does not exist')
    db.delete(user)
    db.commit()
    return True

@router.post('/deactivate')
def deactivate_user(username: str, db: Session = Depends(get_db), current_user: UserSignIn = Depends(get_user_from_token("access_token"))):
    if current_user.Role != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
            detail=f'You are not an admin')
    user = db.query(User).filter(User.Username == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
            detail=f'User with username {username} does not exist')
    user.Status = 'inactive'
    db.add(user)
    db.commit()
    db.refresh(user)
    return True

@router.post('/activate')
def activate_user(username: str, db: Session = Depends(get_db), current_user: UserSignIn = Depends(get_user_from_token("access_token"))):
    if current_user.Role != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
            detail=f'You are not an admin')
    user = db.query(User).filter(User.Username == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
            detail=f'User with username {username} does not exist')
    user.Status = 'active'
    db.add(user)
    db.commit()
    db.refresh(user)
    return True

@router.post("/update", response_model=UserDisplay)
async def update_user_info(
    username: str, 
    request: UserUpdate,
    db: Session = Depends(get_db),
    current_user: UserSignIn = Depends(get_user_from_token("access_token"))
):
    if current_user.Role != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
            detail=f'You are not an admin')
    
    # await user_functions.validate_user_update_data(db, request.role, request.status, request.specjalista)
    if request.specjalista:
        await validate_specialist_types(db, request.specjalista)

    user = db.query(User).filter(User.Username == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
            detail=f'User with username {username} does not exist')
    if request.full_name:
        user.Full_name = request.full_name
    if request.specjalista:
        user.Specjalista = request.specjalista
    if request.role:
        user.Role = request.role
    if request.status:
        user.Status = request.status
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.get("/valid-values")
async def get_valid_values(
    db: Session = Depends(get_db),
    current_user: UserSignIn = Depends(get_user_from_token("access_token"))
):
    if current_user.Role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You are not an admin'
        )
    # Get specialist types from possible_values table
    specialist_types = db.query(PossibleValues)\
        .filter(PossibleValues.Variable_name == "Specjalista")\
        .first()

    return {
        "roles": [r.value for r in RoleEnum],
        "statuses": [s.value for s in StatusEnum],
        "specialist_types": list(specialist_types.Possible_values.keys()) if specialist_types else []
    }


@router.post("/import-csv")
async def import_users_from_file( # async to handle file upload using fastapi's FileUpload
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        # Read file content into memory
        content = await file.read()
        file_object = BytesIO(content)
        
        # Process the file
        users = import_users_from_csv_simple(file_object)
        
        # Import users to database
        results = {
            "success": 0,
            "errors": []
        }
        
        for user in users:
            try:
                user_functions.create_user(db, user)
                results["success"] += 1
            except Exception as e:
                results["errors"].append(f"Error creating user {user.username}: {str(e)}")
        
        return results
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error processing file: {str(e)}"
        )
