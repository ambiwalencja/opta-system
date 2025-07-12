
# from fastapi import HTTPException, status
from db_models.user_data import User
from schemas.user_schemas import UserBase
from sqlalchemy.orm.session import Session
from auth.hashing import Hash
from datetime import datetime

def create_user(db: Session, request: UserBase):
    new_user = User(
        Username = request.username,
        Password = Hash.bcrypt(request.password),
        Role = request.role,
        Created = datetime.now(),
        Last_modified = datetime.now(),
        Last_login = None
        # ID_uzytkownika = 0 #? kto, admin? # to muszę wyciągnąć z access tokena - każde
        # dwa tworzenia użytkownika (dwa endpointy) - jedno z backendu z passphrasem, a drugie z UI
        # dependency - depends on - coś w autoryzacji - z access tokenu możemy wyczytać który to użytkownik
        # EDIT - wykomentowałam to, bo przecież to jest ID tego rekordu, primary key, a nie id creatora, to się ustawia samo, a nie 
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user