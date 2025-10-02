from sqlalchemy.orm.session import Session
from fastapi import HTTPException, status as http_status
from db_models.config import PossibleValues


async def validate_specialist_types(db: Session, specjalista: list[str]) -> None:
    valid_specialists = db.query(PossibleValues)\
            .filter(PossibleValues.Variable_name == "Specjalista")\
            .first()
        
    if not valid_specialists:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not validate Specjalista - no data found for valid specialist types"
        )
        
    valid_specialist_types = valid_specialists.Possible_values.keys()
    
    for spec in specjalista:
        if spec not in valid_specialist_types:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid specialist type: {spec}. Must be one of: {list(valid_specialist_types)}"
            )