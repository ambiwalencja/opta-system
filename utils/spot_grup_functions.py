from fastapi import HTTPException, status
from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm.session import Session
from typing import Optional
import logging

from db_models.client_data import Grupa, SpotkanieGrupowe, UczestnikGrupy, obecni_uczestnicy_spotkania, Pacjent
from schemas.spot_grup_schemas import  SpotkanieGrupoweCreate, SpotkanieGrupoweUpdate

logger = logging.getLogger("opta_system_logger")

def get_spotkanie_by_id(db: Session, id_spotkania: int):
    try:
        
        spotkanie = db.query(SpotkanieGrupowe).filter(SpotkanieGrupowe.ID_spotkania == id_spotkania).first()
        if not spotkanie:
            logger.warning("Spotkanie grupowe with ID %d not found", id_spotkania)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Spotkanie grupowe with ID {id_spotkania} not found")
        obecni_count = db.query(func.count(obecni_uczestnicy_spotkania.c.ID_uczestnika_grupy)).filter(obecni_uczestnicy_spotkania.c.ID_spotkania == id_spotkania).scalar()
        spotkanie.Obecni_uczestnicy_count = obecni_count
        grupa = db.query(Grupa).filter(Grupa.ID_grupy == spotkanie.ID_grupy).first()
        spotkanie.Nazwa_grupy = grupa.Nazwa_grupy
        # Get participants with their pacjent details
        obecni_uczestnicy_list = db.query(
            UczestnikGrupy.ID_uczestnika_grupy,
            Pacjent.ID_pacjenta,
            Pacjent.Imie,
            Pacjent.Nazwisko
        ).join(Pacjent).join( # w join pacjent nie ma "on" - ale to dziła dobrze
            obecni_uczestnicy_spotkania,
            UczestnikGrupy.ID_uczestnika_grupy == obecni_uczestnicy_spotkania.c.ID_uczestnika_grupy
        ).filter(
            obecni_uczestnicy_spotkania.c.ID_spotkania == id_spotkania
        ).all()
        spotkanie.Obecni_uczestnicy = [
            {
                "ID_uczestnika_grupy": id_uczestnika,
                "ID_pacjenta": id_pacjenta,
                "Imie": imie,
                "Nazwisko": nazwisko
            }
            for id_uczestnika, id_pacjenta, imie, nazwisko in obecni_uczestnicy_list
        ]
        logger.debug("Spotkanie grupowe with ID %d retrieved successfully", id_spotkania)
        return spotkanie
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error retrieving spotkanie grupowe with ID %d: %s", id_spotkania, str(e), exc_info=True)
        raise

def create_spotkanie_grupowe(db: Session, spotkanie_data: SpotkanieGrupoweCreate, id_uzytkownika: int):
    try:
        logger.info("Creating new spotkanie grupowe for user ID: %d", id_uzytkownika)
        data_dict = spotkanie_data.model_dump(by_alias=True, exclude={'obecni_uczestnicy'})
        data_dict["Created"] = datetime.now()
        data_dict["Last_modified"] = datetime.now()
        data_dict["ID_uzytkownika"] = id_uzytkownika
        new_spotkanie = SpotkanieGrupowe(**data_dict)
        
        db.add(new_spotkanie)
        db.flush()  # Flush to generate the ID without committing
        
        id_obecnych_uczestnikow = spotkanie_data.obecni_uczestnicy or [] # or [] - co to tu robi?
        if id_obecnych_uczestnikow:
            # print(f'id obecnych uczestników (input): {id_obecnych_uczestnikow}')
            # poniższa wykomentowana część to moje poprzednie rozwiązanie
            # uczestnik_to_add = db.query(UczestnikGrupy).filter(UczestnikGrupy.ID_uczestnika_grupy.in_(id_obecnych_uczestnikow)).all()
            # print(f'Number of uczestnik_to_add: {len(uczestnik_to_add)}')
            # print(f'uczestnik_to_add IDs: {[u.ID_uczestnika_grupy for u in uczestnik_to_add]}')
            # # TODO; dodać sprawdzenie, czy uczestnik o danym id na pewno jest w tej grupie
            # new_spotkanie.obecni_uczestnicy.extend(uczestnik_to_add)
            # print(f'new spotkanie obecni uczestnicy IDs after extend: {[u.ID_uczestnika_grupy for u in new_spotkanie.obecni_uczestnicy]}')
            
            # poniższy fragment zaproponowany przez copilota
            # Insert directly into association table instead of using relationship collection
            for uczestnik_id in id_obecnych_uczestnikow:
                # Verify the uczestnik actually exists first
                uczestnik = db.query(UczestnikGrupy).filter(UczestnikGrupy.ID_uczestnika_grupy == uczestnik_id).first()
                if not uczestnik:
                    logger.warning("UczestnikGrupy with ID %d does not exist", uczestnik_id)
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                                      detail=f"UczestnikGrupy with ID {uczestnik_id} not found")
                # Insert into association table using raw SQL
                stmt = obecni_uczestnicy_spotkania.insert().values(
                    ID_uczestnika_grupy=uczestnik_id,
                    ID_spotkania=new_spotkanie.ID_spotkania
                )
                db.execute(stmt)
                print(f'Added ID {uczestnik_id} to association table')
        db.commit()
        db.refresh(new_spotkanie)
        logger.info("Spotkanie grupowe created successfully with ID: %d", new_spotkanie.ID_spotkania)
        return new_spotkanie
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error creating spotkanie grupowe: %s", str(e), exc_info=True)
        raise

def update_spotkanie_grupowe(db: Session, id_spotkania: int, spotkanie_data: SpotkanieGrupoweUpdate):
    try:
        logger.info("Updating spotkanie grupowe with ID: %d", id_spotkania)
        data_dict = spotkanie_data.model_dump(by_alias=True, exclude={'obecni_uczestnicy'}, exclude_unset=True)
        data_dict["Last_modified"] = datetime.now()
        # spotkanie = get_spotkanie_by_id(db, id_spotkania)
        spotkanie = db.query(SpotkanieGrupowe).filter(SpotkanieGrupowe.ID_spotkania == id_spotkania).first()

        for key, value in data_dict.items():
            setattr(spotkanie, key, value)
        
        db.commit()
        db.refresh(spotkanie)
        logger.info("Spotkanie grupowe with ID %d updated successfully", id_spotkania)
        return spotkanie
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error updating spotkanie grupowe with ID %d: %s", id_spotkania, str(e), exc_info=True)
        raise

def delete_spotkanie_grupowe(db: Session, id_spotkania: int):
    try:
        spotkanie = get_spotkanie_by_id(db, id_spotkania)
        db.delete(spotkanie)
        db.commit()
        logger.info("Spotkanie grupowe with ID %d deleted successfully", id_spotkania)
        return {"detail": f"Spotkanie grupowe with ID {id_spotkania} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error deleting spotkanie grupowe with ID %d: %s", id_spotkania, str(e), exc_info=True)
        raise

def get_all_spotkania_grupowe(db: Session, id_grupy: Optional[int] = None):
    try:
        query = (
            db.query(
                SpotkanieGrupowe,
                func.count(obecni_uczestnicy_spotkania.c.ID_uczestnika_grupy),
                Grupa.Nazwa_grupy
                )
            .outerjoin(obecni_uczestnicy_spotkania) # We use an outer join so that if a meeting has zero participants, it still shows up in your list with a count of 0.
            .outerjoin(Grupa)
            .group_by(SpotkanieGrupowe.ID_spotkania, Grupa.Nazwa_grupy)
        ) #result: list of tuples (SpotkanieGrupowe, count_obecni_uczestnicy) because it's a group_by result
        
        if id_grupy:
            query = query.filter(SpotkanieGrupowe.ID_grupy == id_grupy)
        spotkania = query.all()
        logger.info("All spotkania grupowe retrieved successfully, count: %d", len(spotkania))
        results = []
        for spotkanie, count, nazwa_grupy in spotkania:
            logger.debug("Spotkanie ID: %d, Obecni uczestnicy count: %d, Nazwa grupy: %s", spotkanie.ID_spotkania, count, nazwa_grupy)
            spotkanie.Obecni_uczestnicy_count = count # new parameter added to SpotkanieGrupowe model
            spotkanie.Nazwa_grupy = nazwa_grupy # new parameter added to SpotkanieGrupowe model
            results.append(spotkanie)
        return results
    except Exception as e:
        logger.error("Error retrieving all spotkania grupowe: %s", str(e), exc_info=True)
        raise

