from datetime import date
from sqlalchemy.orm.session import Session
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query as FastapiQuery

from db.db_connect import get_db
from auth.oauth2 import get_user_from_token
from db_models.user_data import User
from schemas.user_schemas import UserSignIn
from utils import pacjent_functions, report_functions, report_variables_lists


router = APIRouter(
    prefix="/report_wizyty",
    tags=["report_wizyty"],
    responses={404: {"description": "Not found"}},
)

@router.get('/wizyty_counts')
def get_wizyty_counts(db: Session = Depends(get_db), 
                       current_user: UserSignIn = Depends(get_user_from_token("access_token")),
                        start: Optional[date] = FastapiQuery(None, description="Start date (YYYY-MM-DD)"),
                        end: Optional[date] = FastapiQuery(None, description="End date (YYYY-MM-DD)")):
    if current_user.Role != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not an admin")
    date_range = (start, end) if start and end else None
    wizyty_counts = report_functions.get_pacjent_counts_by_year(db, date_range)
    return wizyty_counts
