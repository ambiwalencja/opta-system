from sqlalchemy.orm.session import Session
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query as FastapiQuery
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate

from db.db_connect import get_db
from auth.oauth2 import get_user_from_token
from schemas.pacjent_schemas import PacjentCreateBasic, PacjentCreateForm, PacjentDisplay, PacjentUpdate
# from schemas.wizyta_schemas import WizytaIndywidualnaCreate, WizytaIndywidualnaDisplay
# from schemas.grupa_schemas import CreateGrupa, DisplayGrupa
# from db_models.client_data import Pacjent
from db_models.user_data import User
from utils import pacjent_functions


router = APIRouter(
    prefix="/pacjent",
    tags=["pacjent"],
    responses={404: {"description": "Not found"}},
)

@router.post('/create_basic', response_model=PacjentDisplay) # passphrase?
def create_pacjent_1(request: PacjentCreateBasic, db: Session = Depends(get_db), current_user: User = Depends(get_user_from_token("access_token"))):
    return pacjent_functions.create_pacjent_basic(db, request, current_user.ID_uzytkownika)

@router.post('/create_form')
def create_pacjent_2(id_pacjenta: int, request: PacjentCreateForm, db: Session = Depends(get_db), current_user: User = Depends(get_user_from_token("access_token"))):
    return pacjent_functions.create_pacjent_form(db, id_pacjenta, request)

@router.put('/update/{id_pacjenta}') # jesli to ma być wykorzystane do merge to musi zwracać całego pacjenta
def update_pacjent(id_pacjenta: int, request: PacjentUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_user_from_token("access_token"))):
    return pacjent_functions.update_pacjent(db, id_pacjenta, request)

@router.get('/get/{id_pacjenta}') # musi zwracać całego pacjenta
def get_pacjent(id_pacjenta: int, db: Session = Depends(get_db), current_user: User = Depends(get_user_from_token("access_token"))):
    return pacjent_functions.get_pacjent_by_id(db, id_pacjenta)

@router.delete('/delete/{id_pacjenta}')
def delete_pacjent(id_pacjenta: int, db: Session = Depends(get_db), current_user: User = Depends(get_user_from_token("access_token"))):
    return pacjent_functions.delete_pacjent(db, id_pacjenta)

@router.get('/search', response_model=list[PacjentDisplay])
def search_pacjenci(query: str, db: Session = Depends(get_db), current_user: User = Depends(get_user_from_token("access_token"))):
    return pacjent_functions.search_pacjenci(db, query)

@router.get('/all', response_model=Page[PacjentDisplay])
def show_pacjent_list(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_user_from_token("access_token")),
    sort_by: str = FastapiQuery(None, description="Field to sort by"),
    sort_direction: str = FastapiQuery(None, description="'asc' or 'desc'"),
    search_term: Optional[str] = FastapiQuery(None, description="Search in name, email, phone"),
    filters: Optional[List[str]] = FastapiQuery(None, description="Filters as 'field:value' pairs. If it's a date range, write second date in the same pair, after a comma")
    ):
    return pacjent_functions.get_all_pacjenci(db, sort_by, sort_direction, search_term, filters)