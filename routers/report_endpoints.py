from datetime import date
from sqlalchemy.orm.session import Session
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query as FastapiQuery

from db.db_connect import get_db
from auth.oauth2 import get_user_from_token
from db_models.user_data import User
from schemas.user_schemas import UserSignIn
from utils import pacjent_functions, report_functions


router = APIRouter(
    prefix="/report",
    tags=["report"],
    responses={404: {"description": "Not found"}},
)

@router.get('/pacjent_counts')
def get_pacjent_counts_by_year(db: Session = Depends(get_db), 
                       current_user: UserSignIn = Depends(get_user_from_token("access_token")), 
                        # date_range: Optional[List[str]] = FastapiQuery(None, description="Date range as ['YYYY-MM-DD','YYYY-MM-DD']"),
                        start: Optional[date] = FastapiQuery(None, description="Start date (YYYY-MM-DD)"),
                        end: Optional[date] = FastapiQuery(None, description="End date (YYYY-MM-DD)")):
    # if not current_user.is_admin:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not an admin")
    date_range = (start, end) if start and end else None
    return report_functions.get_pacjent_counts_by_year(db, date_range)

@router.get('/plec')
def get_plec_counts(db: Session = Depends(get_db), 
                       current_user: UserSignIn = Depends(get_user_from_token("access_token")),
                       start: Optional[date] = FastapiQuery(None, description="Start date (YYYY-MM-DD)"),
                        end: Optional[date] = FastapiQuery(None, description="End date (YYYY-MM-DD)")):
    # if not current_user.is_admin:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not an admin")
    date_range = (start, end) if start and end else None
    return report_functions.get_plec_counts(db, date_range)