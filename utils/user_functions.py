import logging
from sqlalchemy.orm.session import Session
from fastapi import HTTPException, status as http_status
from datetime import datetime

from auth.hashing import Hash
from db_models.user_data import User
from schemas.user_schemas import UserBase

logger = logging.getLogger("opta_system_logger")


async def create_user(db: Session, request: UserBase):
    try:
        logger.info("Creating new user with username: %s", request.username)
        new_user = User(
            Full_name = request.full_name,
            Username = request.username,
            Password = Hash.bcrypt(request.password),
            Role = request.role,
            Specjalista = request.specjalista,
            Status = request.status, # może to być, tylko na froncie nie będzie używane
            Created = datetime.now(),
            Last_modified = datetime.now(),
            Last_login = None
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        logger.info("User %s created successfully with ID: %s", request.username, new_user.ID_uzytkownika)
        return new_user
    except Exception as e:
        logger.error("Error creating user %s: %s", request.username, str(e), exc_info=True)
        raise

def get_user_by_username(db: Session, username: str):
    try:
        user = db.query(User).filter(User.Username == username).first()
        if not user:
            logger.warning("User lookup failed: username '%s' not found", username)
            raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND,
            detail=f'User with username {username} not found')
        logger.info("User %s retrieved successfully", username)
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error retrieving user %s: %s", username, str(e), exc_info=True)
        raise

def update_last_login(db: Session, user: User):
    try:
        user.Last_login = datetime.now() # to jest utc
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info("Last login updated for user %s", user.Username)
    except Exception as e:
        logger.error("Error updating last login for user %s: %s", user.Username, str(e), exc_info=True)
        raise 

def format_datetime(dt: datetime) -> str:
    if not dt:
        return None
    # Optional: Convert to local timezone - using from zoneinfo import ZoneInfo  # Python 3.9+
    # local_dt = dt.astimezone(ZoneInfo("Europe/Warsaw"))  # or your desired timezone
    # TODO: dodać konwersję na czas lokalny - ale jak się wyklaruje, jak obsługujemy datę - Wojtek sprawdzi, jak mu będzie wygodnie do wyświetlania daty na froncie
    # nie konwertować czasu  w kodzie, tylko wyciągać z zegara maszyny, na której backend stoi - to zrobić w update tiem i w create user
    # jeśli będzie taka funkcja wykorzystaywana w innych schemach też, to przenieść do osobnego pliku
    return dt.strftime("%d.%m.%Y, %H:%M")

def get_recently_active_users(db: Session, limit: int = 10):
    try:
        user_list = (
            db.query(User)
            .filter(User.Last_login != None)
            .order_by(User.Last_login.desc())
            .limit(limit)
            .all()
        )
        logger.info("Retrieved %d recently active users (limit: %d)", len(user_list), limit)
        for user in user_list:
            logger.debug("User %s: Last login: %s", user.Username, user.Last_login)
        return user_list
    except Exception as e:
        logger.error("Error retrieving recently active users: %s", str(e), exc_info=True)
        raise

# async def validate_user_update_data(
#     db: Session,
#     role: Optional[str],
#     status: Optional[str],
#     specjalista: Optional[list[str]]
# ) -> None:
#     if role and role not in [r.value for r in RoleEnum]:
#         raise HTTPException(
#             status_code=http_status.HTTP_400_BAD_REQUEST,
#             detail=f"Invalid role. Must be one of: {[r.value for r in RoleEnum]}"
#         )
    
#     if status and status not in [s.value for s in StatusEnum]:
#         raise HTTPException(
#             status_code=http_status.HTTP_400_BAD_REQUEST,
#             detail=f"Invalid status. Must be one of: {[s.value for s in StatusEnum]}"
#         )
    
#     if specjalista:
#         # Get valid specialist types from possible_values table
#         await validate_specialist_types(db, specjalista)


