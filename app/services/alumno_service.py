from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.models import Alumno
from app import schemas

def create_alumno(db: Session, alumno: schemas.AlumnoCreate):
    """
    Crea un nuevo alumno en la base de datos
    """
    db_alumno = Alumno(**alumno.dict())
    try:
        db.add(db_alumno)
        db.commit()
        db.refresh(db_alumno)
        return db_alumno
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error al crear el alumno")

def get_alumnos(db: Session, skip: int = 0, limit: int = 100):
    """
    Obtiene la lista de alumnos con paginación
    """
    return db.query(Alumno).offset(skip).limit(limit).all()

def get_alumno(db: Session, alumno_id: int):
    """
    Obtiene un alumno por su ID
    """
    return db.query(Alumno).filter(Alumno.id == alumno_id).first()

def update_alumno(db: Session, alumno_id: int, alumno: schemas.AlumnoCreate):
    """
    Actualiza los datos de un alumno
    """
    db_alumno = get_alumno(db, alumno_id)
    if not db_alumno:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")
    
    try:
        for key, value in alumno.dict().items():
            setattr(db_alumno, key, value)
        db.commit()
        db.refresh(db_alumno)
        return db_alumno
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error al actualizar el alumno")

def delete_alumno(db: Session, alumno_id: int):
    """
    Elimina un alumno de la base de datos
    """
    db_alumno = get_alumno(db, alumno_id)
    if not db_alumno:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")
    
    try:
        db.delete(db_alumno)
        db.commit()
        return {"message": "Alumno eliminado correctamente"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error al eliminar el alumno")