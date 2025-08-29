
from db_models.user_data import User
from schemas.user_schemas import UserBase
from sqlalchemy.orm.session import Session
from auth.hashing import Hash
from datetime import datetime
from fastapi import HTTPException, status

def create_user(db: Session, request: UserBase):
    new_user = User(
        Username = request.username,
        Password = Hash.bcrypt(request.password),
        Role = request.role,
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
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