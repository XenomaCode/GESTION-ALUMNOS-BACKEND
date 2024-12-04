from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.models import Calificacion, Alumno, Materia
from app import schemas


def create_calificacion(db: Session, calificacion: schemas.CalificacionCreate):
    """
    Registra una nueva calificación
    """
    # Verificar que existan el alumno y la materia
    alumno = db.query(Alumno).filter(Alumno.id == calificacion.alumno_id).first()
    materia = db.query(Materia).filter(Materia.id == calificacion.materia_id).first()
    
    if not alumno:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")
    if not materia:
        raise HTTPException(status_code=404, detail="Materia no encontrada")
    
    # Verificar que el alumno esté inscrito en la materia
    if materia not in alumno.materias:
        raise HTTPException(status_code=400, detail="El alumno no está inscrito en esta materia")
    
    # Verificar si ya existe una calificación para esta combinación alumno-materia
    existing_calificacion = db.query(Calificacion).filter(
        Calificacion.alumno_id == calificacion.alumno_id,
        Calificacion.materia_id == calificacion.materia_id
    ).first()
    
    if existing_calificacion:
        raise HTTPException(status_code=400, detail="Ya existe una calificación para este alumno en esta materia")
    
    try:
        db_calificacion = Calificacion(**calificacion.dict())
        db.add(db_calificacion)
        db.commit()
        db.refresh(db_calificacion)
        return db_calificacion
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error al registrar la calificación")

def get_calificaciones_alumno(db: Session, alumno_id: int):
    """
    Obtiene todas las calificaciones de un alumno
    """
    alumno = db.query(Alumno).filter(Alumno.id == alumno_id).first()
    if not alumno:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")
    
    calificaciones = db.query(Calificacion).filter(Calificacion.alumno_id == alumno_id).all()
    return calificaciones

def update_calificacion(db: Session, alumno_id: int, materia_id: int, nueva_calificacion: float):
    """
    Actualiza la calificación de un alumno en una materia
    """
    calificacion = db.query(Calificacion).filter(
        Calificacion.alumno_id == alumno_id,
        Calificacion.materia_id == materia_id
    ).first()
    
    if not calificacion:
        raise HTTPException(status_code=404, detail="Calificación no encontrada")
    
    try:
        calificacion.calificacion = nueva_calificacion
        db.commit()
        db.refresh(calificacion)
        return calificacion
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error al actualizar la calificación")

def get_promedio_alumno(db: Session, alumno_id: int):
    """
    Calcula el promedio de un alumno
    """
    calificaciones = get_calificaciones_alumno(db, alumno_id)
    if not calificaciones:
        return 0.0
    
    total = sum(c.calificacion for c in calificaciones)
    return total / len(calificaciones)

def get_todas_calificaciones(db: Session, skip: int = 0, limit: int = 100):
    """
    Obtiene todas las calificaciones de la base de datos
    """
    return db.query(Calificacion).offset(skip).limit(limit).all()