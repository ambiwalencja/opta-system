from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError # pip install python-jose[cryptography]
from fastapi import HTTPException, Depends, status
from sqlalchemy.orm import Session
from db.db_connect import get_db
from utils import user_functions
import os
import logging
from db_models.user_data import User

logger = logging.getLogger("opta_system_logger")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="user/login_form", )

SECRET_KEY = os.environ.get('SECRET_KEY')
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get('ACCESS_TOKEN_EXPIRE_MINUTES'))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.environ.get('REFRESH_TOKEN_EXPIRE_DAYS'))

# tworzenie tokena
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # tutaj jest timezone.utc - w innych miejscach mamy po prostu datetime.now
    # możliwe, że ktoś, np mama, będzie się logować z kraju z inną strefą, więc dobrze byłoby to obsłużyć. ale chyba na ten moment nie trzeba
    to_encode.update({"exp": expire, "scope": "access_token"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict):
  to_encode = data.copy()
  expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
  to_encode.update({"exp": expire, "scope": "refresh_token"})
  encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
  return encoded_jwt

# weryfikacja tokena/tożsamości
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
  credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
  )
  try:
    logger.debug("Attempting to decode access token")
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    username: str = payload.get("username")
    if username is None:
      logger.warning("Token validation failed: no username in payload")
      raise credentials_exception
    logger.debug("Token decoded successfully for user: %s", username)
  except JWTError as e:
    logger.warning("JWT validation error: %s", str(e))
    raise credentials_exception
  
  user = user_functions.get_user_by_username(db, username=username)
  if user is None:
    logger.warning("User not found in database: %s", username)
    raise credentials_exception
  
  logger.debug("User authenticated successfully: %s", username)
  return user

# weryfikacja tokenu/tożsamości - ver 2 - obsługująca access i refresh token
def get_user_from_token_raw(token: str, expected_scope: str, db: Session) -> User:
    try:
        logger.debug("Validating token with expected scope: %s", expected_scope)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_scope = payload.get("scope")
        if token_scope != expected_scope:
            logger.warning("Invalid token scope. Expected: %s, Got: %s", expected_scope, token_scope)
            raise JWTError("Invalid token scope")
        logger.debug("Token scope validation passed")
    except JWTError as e:
        logger.warning("Token validation failed: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    username = payload.get("username")
    if not username:
        logger.warning("Token validation failed: missing username in token")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing username in token")
    
    logger.debug("Looking up user: %s", username)
    user = user_functions.get_user_by_username(db, username=username)
    if user is None:
        logger.warning("User not found in database: %s", username)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    
    logger.debug("User authenticated successfully with %s token: %s", expected_scope, username)
    return user

def get_user_from_token(expected_scope: str):
    def dependency(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
        return get_user_from_token_raw(token, expected_scope, db)
    return dependency