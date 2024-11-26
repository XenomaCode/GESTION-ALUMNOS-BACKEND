from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.models import Materia
from app import schemas

def create_materia(db: Session, materia: schemas.MateriaCreate):
    """
    Crea una nueva materia en la base de datos
    """
    db_materia = Materia(**materia.dict())
    try:
        db.add(db_materia)
        db.commit()
        db.refresh(db_materia)
        return db_materia
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error al crear la materia")

def get_materias(db: Session, skip: int = 0, limit: int = 100):
    """
    Obtiene la lista de materias con paginación
    """
    return db.query(Materia).offset(skip).limit(limit).all()

def get_materia(db: Session, materia_id: int):
    """
    Obtiene una materia por su ID
    """
    return db.query(Materia).filter(Materia.id == materia_id).first()

def update_materia(db: Session, materia_id: int, materia: schemas.MateriaCreate):
    """
    Actualiza los datos de una materia
    """
    db_materia = get_materia(db, materia_id)
    if not db_materia:
        raise HTTPException(status_code=404, detail="Materia no encontrada")
    
    try:
        for key, value in materia.dict().items():
            setattr(db_materia, key, value)
        db.commit()
        db.refresh(db_materia)
        return db_materia
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error al actualizar la materia")

def delete_materia(db: Session, materia_id: int):
    """
    Elimina una materia de la base de datos
    """
    db_materia = get_materia(db, materia_id)
    if not db_materia:
        raise HTTPException(status_code=404, detail="Materia no encontrada")
    
    try:
        db.delete(db_materia)
        db.commit()
        return {"message": "Materia eliminada correctamente"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error al eliminar la materia")