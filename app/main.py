from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas
from app.db.database import engine, get_db
from app.services import (
    auth_service,
    jwt_service,
    alumno_service,
    materia_service,
    inscripcion_service,
    calificacion_service
)

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Sistema de Gestión Escolar",
    description="API para gestionar alumnos, materias, inscripciones y calificaciones",
    version="1.0.0"
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    email = jwt_service.verify_token(token)
    user = auth_service.get_user_by_email(db, email=email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

@app.post("/token", response_model=schemas.Token, tags=["Autenticación"])
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Obtener token de acceso mediante credenciales de usuario
    """
    user = auth_service.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = jwt_service.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

# CRUD Alumnos
@app.post("/alumnos/", response_model=schemas.Alumno, tags=["Alumnos"])
def create_alumno(
    alumno: schemas.AlumnoCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """
    Crear un nuevo alumno con la siguiente información:
    - nombre: Nombre del alumno
    - apellido: Apellido del alumno
    - matricula: Matrícula única del alumno
    - email: Correo electrónico del alumno
    """
    return alumno_service.create_alumno(db, alumno)

@app.get("/alumnos/", response_model=List[schemas.Alumno], tags=["Alumnos"])
def read_alumnos(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """
    Obtener lista de todos los alumnos registrados
    """
    return alumno_service.get_alumnos(db, skip=skip, limit=limit)

@app.get("/alumnos/{alumno_id}", response_model=schemas.Alumno, tags=["Alumnos"])
def read_alumno(
    alumno_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """
    Obtener información detallada de un alumno específico
    """
    alumno = alumno_service.get_alumno(db, alumno_id)
    if alumno is None:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")
    return alumno

@app.put("/alumnos/{alumno_id}", response_model=schemas.Alumno, tags=["Alumnos"])
def update_alumno(
    alumno_id: int,
    alumno: schemas.AlumnoCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """
    Actualizar información de un alumno existente
    """
    return alumno_service.update_alumno(db, alumno_id, alumno)

@app.delete("/alumnos/{alumno_id}", tags=["Alumnos"])
def delete_alumno(
    alumno_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """
    Eliminar un alumno del sistema
    """
    return alumno_service.delete_alumno(db, alumno_id)

# CRUD Materias
@app.post("/materias/", response_model=schemas.Materia, tags=["Materias"])
def create_materia(
    materia: schemas.MateriaCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """
    Crear una nueva materia con la siguiente información:
    - nombre: Nombre de la materia
    - codigo: Código único de la materia
    - creditos: Número de créditos de la materia
    """
    return materia_service.create_materia(db, materia)

@app.get("/materias/", response_model=List[schemas.Materia], tags=["Materias"])
def read_materias(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """
    Obtener lista de todas las materias registradas
    """
    return materia_service.get_materias(db, skip=skip, limit=limit)

@app.get("/materias/{materia_id}", response_model=schemas.Materia, tags=["Materias"])
def read_materia(
    materia_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """
    Obtener información detallada de una materia específica
    """
    materia = materia_service.get_materia(db, materia_id)
    if materia is None:
        raise HTTPException(status_code=404, detail="Materia no encontrada")
    return materia

@app.put("/materias/{materia_id}", response_model=schemas.Materia, tags=["Materias"])
def update_materia(
    materia_id: int,
    materia: schemas.MateriaCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """
    Actualizar información de una materia existente
    """
    return materia_service.update_materia(db, materia_id, materia)

@app.delete("/materias/{materia_id}", tags=["Materias"])
def delete_materia(
    materia_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """
    Eliminar una materia del sistema
    """
    return materia_service.delete_materia(db, materia_id)

# Inscripciones
@app.post("/inscripcion/{alumno_id}/{materia_id}", tags=["Inscripciones"])
def inscribir_alumno(
    alumno_id: int,
    materia_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """
    Inscribir un alumno en una materia específica
    """
    return inscripcion_service.inscribir_alumno(db, alumno_id, materia_id)

# Calificaciones
@app.post("/calificaciones/", response_model=schemas.Calificacion, tags=["Calificaciones"])
def create_calificacion(
    calificacion: schemas.CalificacionCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """
    Registrar una calificación para un alumno en una materia específica
    """
    return calificacion_service.create_calificacion(db, calificacion)

@app.get("/calificaciones/{alumno_id}", tags=["Calificaciones"])
def get_calificaciones_alumno(
    alumno_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """
    Obtener todas las calificaciones de un alumno específico
    """
    return calificacion_service.get_calificaciones_alumno(db, alumno_id)