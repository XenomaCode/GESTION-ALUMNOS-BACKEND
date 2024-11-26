from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.models import Alumno, Materia
from app import schemas

def inscribir_alumno(db: Session, alumno_id: int, materia_id: int):
    """
    Inscribe un alumno en una materia
    """
    # Verificar que existan tanto el alumno como la materia
    alumno = db.query(Alumno).filter(Alumno.id == alumno_id).first()
    materia = db.query(Materia).filter(Materia.id == materia_id).first()
    
    if not alumno:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")
    if not materia:
        raise HTTPException(status_code=404, detail="Materia no encontrada")
    
    # Verificar que el alumno no esté ya inscrito en la materia
    if materia in alumno.materias:
        raise HTTPException(status_code=400, detail="El alumno ya está inscrito en esta materia")
    
    try:
        alumno.materias.append(materia)
        db.commit()
        return {"message": "Inscripción realizada correctamente"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error al realizar la inscripción")

def get_materias_alumno(db: Session, alumno_id: int):
    """
    Obtiene todas las materias en las que está inscrito un alumno
    """
    alumno = db.query(Alumno).filter(Alumno.id == alumno_id).first()
    if not alumno:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")
    return alumno.materias

def get_alumnos_materia(db: Session, materia_id: int):
    """
    Obtiene todos los alumnos inscritos en una materia
    """
    materia = db.query(Materia).filter(Materia.id == materia_id).first()
    if not materia:
        raise HTTPException(status_code=404, detail="Materia no encontrada")
    return materia.alumnos

def dar_baja_materia(db: Session, alumno_id: int, materia_id: int):
    """
    Da de baja a un alumno de una materia
    """
    alumno = db.query(Alumno).filter(Alumno.id == alumno_id).first()
    materia = db.query(Materia).filter(Materia.id == materia_id).first()
    
    if not alumno:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")
    if not materia:
        raise HTTPException(status_code=404, detail="Materia no encontrada")
    
    if materia not in alumno.materias:
        raise HTTPException(status_code=400, detail="El alumno no está inscrito en esta materia")
    
    try:
        alumno.materias.remove(materia)
        db.commit()
        return {"message": "Alumno dado de baja de la materia correctamente"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error al dar de baja al alumno de la materia")