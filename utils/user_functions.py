
from db_models.user_data import User
from schemas.user_schemas import UserBase, RoleEnum, StatusEnum
from sqlalchemy.orm.session import Session
from auth.hashing import Hash
from datetime import datetime
from fastapi import HTTPException, status as http_status
from db_models.config import PossibleValues
from typing import Optional


def create_user(db: Session, request: UserBase):
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
    return new_user

def get_user_by_username(db: Session, username: str):
    user = db.query(User).filter(User.Username == username).first()
    if not user:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND,
        detail=f'User with username {username} not found')
    return user

def update_last_login(db: Session, user: User):
    user.Last_login = datetime.now() # to jest utc
    db.add(user)
    db.commit()
    db.refresh(user)
    return 

def format_datetime(dt: datetime) -> str:
    if not dt:
        return None
    # Optional: Convert to local timezone - using from zoneinfo import ZoneInfo  # Python 3.9+
    # local_dt = dt.astimezone(ZoneInfo("Europe/Warsaw"))  # or your desired timezone
    # TODO: dodać konwersję na czas lokalny - ale jak się wyklaruje, jak obsługujemy datę - Wojtek sprawdzi, jak mu będzie wygodnie do wyświetlania daty na froncie
    # nie konwertować czasu  w kodzie, tylko wyciągać z zegara maszyny, na której backend stoi - to zrobić w update tiem i w create user
    # jeśli będzie taka funkcja wykorzystaywana w innych schemach też, to przenieść do osobnego pliku
    return dt.strftime("%d.%m.%Y, %H:%M")


async def validate_user_update_data(
    db: Session,
    role: Optional[str],
    status: Optional[str],
    specjalista: Optional[list[str]]
) -> None:
    if role and role not in [r.value for r in RoleEnum]:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {[r.value for r in RoleEnum]}"
        )
    
    if status and status not in [s.value for s in StatusEnum]:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {[s.value for s in StatusEnum]}"
        )
    
    if specjalista:
        # Get valid specialist types from possible_values table
        valid_specialists = db.query(PossibleValues)\
            .filter(PossibleValues.Variable_name == "Specjalista")\
            .first()
        
        if not valid_specialists:
            raise HTTPException(
                status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not validate specialist types"
            )
            
        valid_specialist_types = valid_specialists.Possible_values.keys()
        
        for spec in specjalista:
            if spec not in valid_specialist_types:
                raise HTTPException(
                    status_code=http_status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid specialist type: {spec}. Must be one of: {list(valid_specialist_types)}"
                )
