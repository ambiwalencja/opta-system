from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm.session import Session
from old_db.old_db_connect import get_db as get_db_old
from db.db_connect import get_db as get_db_new
from old_db.data_import import import_table_to_dataframe, import_pacjenci_to_new_db, import_wizyty_ind_to_new_db, import_spotkania_grupowe_to_new_db
from old_db.transform_old_db import transform_imported_table

router = APIRouter(
    prefix="/old_db",
    tags=["old_db"],
    responses={404: {"description": "Not found"}},
)

@router.post('/import')
def import_table(table_name: str, db: Session = Depends(get_db_old)):
    try:
        df = import_table_to_dataframe(table_name, db)
        # return import_table_to_dataframe(table_name, db)
        return True
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error importing table {table_name}: {str(e)}"
        )
    
@router.post('/transform') # pomocniczy endpoint
def transform_table(old_db_table_name: str, new_db_table_name: str, db_old: Session = Depends(get_db_old), db_new: Session = Depends(get_db_new)):
    try:
        df = transform_imported_table(old_db_table_name, new_db_table_name, db_old, db_new)
        # return transform_imported_table(table_name, db)
        return True
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error transforming table {old_db_table_name}: {str(e)}"
        )


@router.post('/import-to-new-db')
def import_to_new_db(old_db_table_name: str, new_db_table_name: str, db_old: Session = Depends(get_db_old), db_new: Session = Depends(get_db_new)):
    try:
        # First transform the data
        df = transform_imported_table(old_db_table_name, new_db_table_name, db_old, db_new)
        
        if old_db_table_name == "pacjenci":
            results = import_pacjenci_to_new_db(df, db_new)
            return {
                "message": f"Import completed. Successfully imported {results['success_count']} patients.",
                "errors": results['errors'] if results['error_count'] > 0 else None
            }
        elif old_db_table_name == "wizyty":
            if new_db_table_name == "wizyty_indywidualne":
                results = import_wizyty_ind_to_new_db(df, db_new)
                return {
                    "message": f"Import completed. Successfully imported {results['success_count']} visits.",
                    "errors": results['errors'] if results['error_count'] > 0 else None
                }
            elif new_db_table_name == "spotkania_grupowe":
                results = import_spotkania_grupowe_to_new_db(df, db_new)
                return {
                    "message": f"Import completed. Successfully imported {results['success_count']} visits.",
                    "errors": results['errors'] if results['error_count'] > 0 else None
                }
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Table {old_db_table_name} import not implemented"
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error during import: {str(e)}"
        )