from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from app import models, schemas
from app.db.database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Sistema de Gestión Escolar",
    description="API para gestionar alumnos, materias, inscripciones y calificaciones",
    version="1.0.0"
)

# Configuración de seguridad
SECRET_KEY = "tu_clave_secreta_aqui"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Funciones de utilidad para autenticación
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    return user

# Rutas agrupadas por tags para mejor organización en Swagger

@app.post("/token", response_model=schemas.Token, tags=["Autenticación"])
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Obtener token de acceso mediante credenciales de usuario
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email})
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
    db_alumno = models.Alumno(**alumno.dict())
    db.add(db_alumno)
    db.commit()
    db.refresh(db_alumno)
    return db_alumno

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
    alumnos = db.query(models.Alumno).offset(skip).limit(limit).all()
    return alumnos

@app.get("/alumnos/{alumno_id}", response_model=schemas.Alumno, tags=["Alumnos"])
def read_alumno(
    alumno_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """
    Obtener información detallada de un alumno específico
    """
    alumno = db.query(models.Alumno).filter(models.Alumno.id == alumno_id).first()
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
    db_alumno = db.query(models.Alumno).filter(models.Alumno.id == alumno_id).first()
    if db_alumno is None:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")
    for key, value in alumno.dict().items():
        setattr(db_alumno, key, value)
    db.commit()
    db.refresh(db_alumno)
    return db_alumno

@app.delete("/alumnos/{alumno_id}", tags=["Alumnos"])
def delete_alumno(
    alumno_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """
    Eliminar un alumno del sistema
    """
    alumno = db.query(models.Alumno).filter(models.Alumno.id == alumno_id).first()
    if alumno is None:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")
    db.delete(alumno)
    db.commit()
    return {"message": "Alumno eliminado"}

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
    db_materia = models.Materia(**materia.dict())
    db.add(db_materia)
    db.commit()
    db.refresh(db_materia)
    return db_materia

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
    materias = db.query(models.Materia).offset(skip).limit(limit).all()
    return materias

@app.get("/materias/{materia_id}", response_model=schemas.Materia, tags=["Materias"])
def read_materia(
    materia_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """
    Obtener información detallada de una materia específica
    """
    materia = db.query(models.Materia).filter(models.Materia.id == materia_id).first()
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
    db_materia = db.query(models.Materia).filter(models.Materia.id == materia_id).first()
    if db_materia is None:
        raise HTTPException(status_code=404, detail="Materia no encontrada")
    for key, value in materia.dict().items():
        setattr(db_materia, key, value)
    db.commit()
    db.refresh(db_materia)
    return db_materia

@app.delete("/materias/{materia_id}", tags=["Materias"])
def delete_materia(
    materia_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """
    Eliminar una materia del sistema
    """
    materia = db.query(models.Materia).filter(models.Materia.id == materia_id).first()
    if materia is None:
        raise HTTPException(status_code=404, detail="Materia no encontrada")
    db.delete(materia)
    db.commit()
    return {"message": "Materia eliminada"}

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
    alumno = db.query(models.Alumno).filter(models.Alumno.id == alumno_id).first()
    materia = db.query(models.Materia).filter(models.Materia.id == materia_id).first()
    
    if not alumno or not materia:
        raise HTTPException(status_code=404, detail="Alumno o materia no encontrados")
        
    alumno.materias.append(materia)
    db.commit()
    return {"message": "Inscripción exitosa"}

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
    db_calificacion = models.Calificacion(**calificacion.dict())
    db.add(db_calificacion)
    db.commit()
    db.refresh(db_calificacion)
    return db_calificacion

@app.get("/calificaciones/{alumno_id}", tags=["Calificaciones"])
def get_calificaciones_alumno(
    alumno_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """
    Obtener todas las calificaciones de un alumno específico
    """
    calificaciones = db.query(models.Calificacion).filter(models.Calificacion.alumno_id == alumno_id).all()
    if not calificaciones:
        raise HTTPException(status_code=404, detail="No se encontraron calificaciones para este alumno")
    return calificaciones