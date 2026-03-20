from sqlalchemy.orm.session import Session
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi import UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm
import os
# from typing import Optional
from io import BytesIO
import logging

from auth.hashing import Hash
from auth.oauth2 import create_access_token, create_refresh_token
from auth.oauth2 import get_user_from_token_raw, get_user_from_token
from db.db_connect import get_db
from db_models.user_data import User
from db_models.config import PossibleValues
from old_db.data_import import import_users_from_csv_simple
from schemas.user_schemas import (
    UserCreate, UserDisplay, UserSignIn, TokenRequest, RoleEnum, 
    StatusEnum, UserUpdate
)
from utils import user_functions
from utils.validation import validate_specialist_types 


REFRESH_TOKEN_EXPIRE_DAYS = int(os.environ.get('REFRESH_TOKEN_EXPIRE_DAYS'))
REFRESH_TOKEN_EXPIRE_SECONDS = REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60

router = APIRouter(
    prefix="/user",
    tags=["user"],
    responses={404: {"description": "Not found"}},
)

logger = logging.getLogger("opta_system_logger")

@router.post('/create/{passphrase}', response_model=UserDisplay)
async def create_user(request: UserCreate, passphrase: str, db: Session = Depends(get_db)):
    try:
        # check passphrase
        if passphrase != os.environ.get('REGISTER_PASSPHRASE'):
            logger.warning("User creation attempt with incorrect passphrase")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                detail='Incorrect passphrase')
        # validate request
        await validate_specialist_types(db, request.specjalista)
        # check if user already exists
        if db.query(User).filter(User.Username == request.username).first():
            logger.warning("User creation attempt for existing username: %s", request.username)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                detail='User already exists')
        logger.info("Creating new user: %s", request.username)
        return await user_functions.create_user(db, request)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error creating user %s: %s", request.username, str(e), exc_info=True)
        raise

@router.post('/login')
def login(request: UserSignIn, db: Session = Depends(get_db)):
    try:
        user = user_functions.get_user_by_username(db, request.username)
        if not Hash.verify(user.Password, request.password):
            logger.warning("Login attempt with incorrect password for user: %s", request.username)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Incorrect password')
        
        access_token = create_access_token(data={'username': user.Username})
        refresh_token = create_refresh_token(data={"username": user.Username})
        
        user_functions.update_last_login(db, user)
        logger.info("User %s logged in successfully.", user.Username)
        return {
            'access_token': access_token,
            "refresh_token": refresh_token,
            'token_type': 'bearer',
            'user_id': user.ID_uzytkownika,
            'username': user.Username,
            'full_name': user.Full_name,
            'role': user.Role
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error during login for user %s: %s", request.username, str(e), exc_info=True)
        raise

@router.post('/login_form') # do testowania, do autoryzacji w docsach
def login_form(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    try:
        user = user_functions.get_user_by_username(db, form_data.username)
        if not Hash.verify(user.Password, form_data.password):
            logger.warning("Login form attempt with incorrect password for user: %s", form_data.username)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Incorrect password')
        
        access_token = create_access_token(data={'username': user.Username})
        refresh_token = create_refresh_token(data={"username": user.Username})
        
        logger.info("User %s logged in via form.", user.Username)
        return {
            'full_name': user.Full_name,
            'access_token': access_token,
            "refresh_token": refresh_token,
            'token_type': 'bearer'
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error during login form for user %s: %s", form_data.username, str(e), exc_info=True)
        raise

@router.post("/refresh")
async def refresh_token(data: TokenRequest, db: Session = Depends(get_db)):
    try:
        refresh_token = data.refresh_token
        if not refresh_token:
            logger.warning("Token refresh attempt without refresh token")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No refresh token")

        user = get_user_from_token_raw(refresh_token, "refresh_token", db)
        new_access_token = create_access_token({"username": user.Username})
        logger.info("Access token refreshed for user %s", user.Username)
        return {"access_token": new_access_token}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error refreshing token: %s", str(e), exc_info=True)
        raise

@router.get("/me", response_model=UserDisplay)
def get_me(current_user: User = Depends(get_user_from_token("access_token"))):
    return current_user

@router.post('/reset')
def reset_password_by_admin(request: UserSignIn, 
                            db: Session = Depends(get_db), 
                            current_user: UserSignIn = Depends(get_user_from_token("access_token"))):
    try:
        user = db.query(User).filter(User.Username == request.username).first()
        if not user:
            logger.warning("Password reset attempt for non-existent user: %s", request.username)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                detail=f'User {request.username} does not exist')
        if current_user.Role != 'admin':
            logger.warning("Unauthorized password reset attempt by user: %s for user: %s", current_user.Username, request.username)
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                detail=f'You are not an admin')
        user.Password = Hash.bcrypt(request.password)
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info("Password reset by admin %s for user %s", current_user.Username, request.username)
        return True
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error resetting password for user %s: %s", request.username, str(e), exc_info=True)
        raise

@router.post('/reset_password_user')
def reset_password_by_user(old_password: str, 
                           new_password: str,
                            db: Session = Depends(get_db),
                           current_user: UserSignIn = Depends(get_user_from_token("access_token"))):
    try:
        user = db.query(User).filter(User.Username == current_user.Username).first()
        if not Hash.verify(user.Password, old_password):
            logger.warning("Password reset attempt with incorrect old password for user %s", current_user.Username)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'Old password is incorrect')
        user.Password = Hash.bcrypt(new_password)
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info("Password reset for user %s", current_user.Username)
        return True
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error resetting password for user %s: %s", current_user.Username, str(e), exc_info=True)
        raise

@router.get('/display')
def display_users(db: Session = Depends(get_db), current_user: UserSignIn = Depends(get_user_from_token("access_token"))):
    try:
        if current_user.Role != 'admin':
            logger.warning("Unauthorized users display attempt by user: %s", current_user.Username)
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                detail=f'You are not an admin')
        logger.info("User %s (admin) displaying user list", current_user.Username)
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
        logger.info("User list displayed by admin %s (%d users)", current_user.Username, len(data))
        return response_data
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error displaying users: %s", str(e), exc_info=True)
        raise

@router.delete('/delete')
def delete_users(username: str, db: Session = Depends(get_db), current_user: UserSignIn = Depends(get_user_from_token("access_token"))): 
    try:
        if current_user.Role != 'admin':
            logger.warning("Unauthorized user delete attempt by user: %s", current_user.Username)
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                detail=f'You are not an admin')
        user = db.query(User).filter(User.Username == username).first()
        if not user:
            logger.warning("Delete attempt for non-existent user: %s", username)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                detail=f'User with username {username} does not exist')
        db.delete(user)
        db.commit()
        logger.info("User %s deleted by admin %s", username, current_user.Username)
        return True
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error deleting user %s: %s", username, str(e), exc_info=True)
        raise

@router.put('/deactivate')
def deactivate_user(username: str, db: Session = Depends(get_db), current_user: UserSignIn = Depends(get_user_from_token("access_token"))):
    try:
        if current_user.Role != 'admin':
            logger.warning("Unauthorized user deactivate attempt by user: %s", current_user.Username)
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                detail=f'You are not an admin')
        user = db.query(User).filter(User.Username == username).first()
        if not user:
            logger.warning("Deactivate attempt for non-existent user: %s", username)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                detail=f'User with username {username} does not exist')
        user.Status = 'inactive'
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info("User %s deactivated by admin %s", username, current_user.Username)
        return True
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error deactivating user %s: %s", username, str(e), exc_info=True)
        raise

@router.put('/activate')
def activate_user(username: str, db: Session = Depends(get_db), current_user: UserSignIn = Depends(get_user_from_token("access_token"))):
    try:
        if current_user.Role != 'admin':
            logger.warning("Unauthorized user activate attempt by user: %s", current_user.Username)
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                detail=f'You are not an admin')
        user = db.query(User).filter(User.Username == username).first()
        if not user:
            logger.warning("Activate attempt for non-existent user: %s", username)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                detail=f'User with username {username} does not exist')
        user.Status = 'active'
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info("User %s activated by admin %s", username, current_user.Username)
        return True
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error activating user %s: %s", username, str(e), exc_info=True)
        raise

@router.put("/update", response_model=UserDisplay)
async def update_user_info(
    username: str, 
    request: UserUpdate,
    db: Session = Depends(get_db),
    current_user: UserSignIn = Depends(get_user_from_token("access_token"))
):
    try:
        if current_user.Role != 'admin':
            logger.warning("Unauthorized user update attempt by user: %s", current_user.Username)
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                detail=f'You are not an admin')
        
        # await user_functions.validate_user_update_data(db, request.role, request.status, request.specjalista)
        if request.specjalista:
            await validate_specialist_types(db, request.specjalista)

        user = db.query(User).filter(User.Username == username).first()
        if not user:
            logger.warning("Update attempt for non-existent user: %s", username)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                detail=f'User with username {username} does not exist')
        
        logger.info("Updating user %s with new information by admin %s", username, current_user.Username)
        if request.full_name:
            user.Full_name = request.full_name
            logger.debug("Updated full_name for user %s", username)
        if request.specjalista:
            user.Specjalista = request.specjalista
            logger.debug("Updated specjalista for user %s", username)
        if request.role:
            user.Role = request.role
            logger.debug("Updated role for user %s", username)
        if request.status:
            user.Status = request.status
            logger.debug("Updated status for user %s", username)
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info("User %s updated successfully by admin %s", username, current_user.Username)
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error updating user %s: %s", username, str(e), exc_info=True)
        raise

@router.get("/valid-values")
async def get_valid_values(
    db: Session = Depends(get_db),
    current_user: UserSignIn = Depends(get_user_from_token("access_token"))
):
    try:
        if current_user.Role != 'admin':
            logger.warning("Unauthorized valid values request by user: %s", current_user.Username)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='You are not an admin'
            )
        logger.info("User %s (admin) retrieving valid values", current_user.Username)
        # Get specialist types from possible_values table
        specialist_types = db.query(PossibleValues)\
            .filter(PossibleValues.Variable_name == "Specjalista")\
            .first()
        logger.info("Valid values retrieved by admin %s", current_user.Username)
        return {
            "roles": [r.value for r in RoleEnum],
            "statuses": [s.value for s in StatusEnum],
            "specialist_types": list(specialist_types.Possible_values.keys()) if specialist_types else []
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error retrieving valid values: %s", str(e), exc_info=True)
        raise


@router.post("/import-csv")
async def import_users_from_file( # async to handle file upload using fastapi's FileUpload
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        logger.info("Starting CSV import from file: %s", file.filename)
        # Read file content into memory
        content = await file.read()
        file_object = BytesIO(content)
        
        # Process the file
        users = import_users_from_csv_simple(file_object)
        logger.info("Parsed %d users from CSV file", len(users))
        
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
                error_msg = f"Error creating user {user.username}: {str(e)}"
                logger.warning(error_msg)
                results["errors"].append(error_msg)
        
        logger.info("CSV import completed: %d users created, %d errors", results['success'], len(results['errors']))
        return results
        
    except Exception as e:
        logger.error("Error processing CSV file %s: %s", file.filename, str(e), exc_info=True)
        raise HTTPException(
            status_code=400,
            detail=f"Error processing file: {str(e)}"
        )
