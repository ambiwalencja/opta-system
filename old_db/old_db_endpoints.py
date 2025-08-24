from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm.session import Session
from old_db.old_db_connect import get_db
from old_db.data_import import import_table_to_dataframe
from old_db.transform_old_db import transform_imported_table

router = APIRouter(
    prefix="/old_db",
    tags=["old_db"],
    responses={404: {"description": "Not found"}},
)

@router.post('/import')
def import_table(table_name: str, db: Session = Depends(get_db)):
    try:
        df = import_table_to_dataframe(table_name, db)
        # return import_table_to_dataframe(table_name, db)
        return True
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error importing table {table_name}: {str(e)}"
        )
    
@router.post('/transform')
def transform_table(table_name: str, db: Session = Depends(get_db)):
    try:
        df = transform_imported_table(table_name, db)
        # return transform_imported_table(table_name, db)
        return True
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error transforming table {table_name}: {str(e)}"
        )