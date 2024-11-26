from fastapi import Body, FastAPI, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional, Annotated
from app.models.models import Base, User
from app.db.database import engine, get_db, SessionLocal
from app import schemas
from app.services import (
    auth_service,
    jwt_service,
    alumno_service,
    materia_service,
    inscripcion_service,
    calificacion_service,
    admin_service
)
from app.middleware.auth_middleware import admin_required

# Crear las tablas
Base.metadata.create_all(bind=engine)

# Inicializar admin
def init_admin():
    db = SessionLocal()
    try:
        admin_service.create_admin(db)
    finally:
        db.close()

init_admin()

app = FastAPI(
    title="Sistema de Gestión Escolar",
    description="API para gestionar alumnos, materias, inscripciones y calificaciones",
    version="1.0.0"
)

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> schemas.User:
    email = jwt_service.verify_token(token)
    user = auth_service.get_user_by_email(db, email=email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return schemas.User.from_orm(user)

# Rutas de autenticación
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
    access_token = jwt_service.create_access_token(data={"sub": user.email, "role": user.role})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": str(user.role)
    }

@app.post("/register", response_model=schemas.User, tags=["Autenticación"])
async def register_user(
    email: Annotated[str, Form(description="Correo electrónico del usuario")],
    password: Annotated[str, Form(description="Contraseña del usuario")],
    role: Annotated[str, Form(description="Rol del usuario (admin/user)")] = "user",
    db: Session = Depends(get_db)
):
    """
    Registrar un nuevo usuario no administrador
    """
    user_data = schemas.UserCreate(email=email, password=password, role=role)
    return auth_service.create_user(db, user_data)

# CRUD Alumnos
@app.post(
    "/alumnos/",
    response_model=schemas.Alumno,
    tags=["Alumnos"],
    summary="Crear nuevo alumno"
)
async def create_alumno(
    nombre: Annotated[str, Form(description="Nombre del alumno (2-50 caracteres)")],
    apellido: Annotated[str, Form(description="Apellido del alumno (2-50 caracteres)")],
    matricula: Annotated[str, Form(description="Matrícula única del alumno (5-20 caracteres)")],
    email: Annotated[str, Form(description="Correo electrónico del alumno")],
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(admin_required)
):
    """
    Crear un nuevo alumno (solo administradores)
    """
    alumno_data = schemas.AlumnoCreate(
        nombre=nombre,
        apellido=apellido,
        matricula=matricula,
        email=email
    )
    return alumno_service.create_alumno(db, alumno_data)

@app.get("/alumnos/", response_model=List[schemas.Alumno], tags=["Alumnos"])
def read_alumnos(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """
    Obtener lista de todos los alumnos registrados (todos los usuarios autenticados)
    """
    return alumno_service.get_alumnos(db, skip=skip, limit=limit)

@app.get("/alumnos/{alumno_id}", response_model=schemas.Alumno, tags=["Alumnos"])
def read_alumno(
    alumno_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """
    Obtener información detallada de un alumno específico (todos los usuarios autenticados)
    """
    try:
        alumno = alumno_service.get_alumno(db, alumno_id)
        return alumno
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/alumnos/{alumno_id}", response_model=schemas.Alumno, tags=["Alumnos"])
async def update_alumno(
    alumno_id: int,
    nombre: Annotated[str, Form(description="Nombre del alumno")] = None,
    apellido: Annotated[str, Form(description="Apellido del alumno")] = None,
    email: Annotated[str, Form(description="Correo electrónico")] = None,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(admin_required)
):
    """
    Actualizar información de un alumno existente (solo administradores)
    """
    alumno_data = schemas.AlumnoUpdate(
        nombre=nombre if nombre else None,
        apellido=apellido if apellido else None,
        email=email if email else None
    )
    return alumno_service.update_alumno(db, alumno_id, alumno_data)

@app.delete("/alumnos/{alumno_id}", response_model=schemas.ResponseMessage, tags=["Alumnos"])
def delete_alumno(
    alumno_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(admin_required)
):
    """
    Eliminar un alumno del sistema (solo administradores)
    """
    return alumno_service.delete_alumno(db, alumno_id)

# CRUD Materias
@app.post("/materias/", response_model=schemas.Materia, tags=["Materias"])
async def create_materia(
    nombre: Annotated[str, Form(description="Nombre de la materia")],
    codigo: Annotated[str, Form(description="Código único de la materia")],
    creditos: Annotated[int, Form(description="Número de créditos")],
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(admin_required)
):
    """
    Crear una nueva materia (solo administradores)
    """
    materia_data = schemas.MateriaCreate(
        nombre=nombre,
        codigo=codigo,
        creditos=creditos
    )
    return materia_service.create_materia(db, materia_data)

@app.get("/materias/", response_model=List[schemas.Materia], tags=["Materias"])
def read_materias(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """
    Obtener lista de todas las materias registradas (todos los usuarios autenticados)
    """
    return materia_service.get_materias(db, skip=skip, limit=limit)

@app.get("/materias/{materia_id}", response_model=schemas.Materia, tags=["Materias"])
def read_materia(
    materia_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """
    Obtener información detallada de una materia específica (todos los usuarios autenticados)
    """
    return materia_service.get_materia(db, materia_id)

@app.put("/materias/{materia_id}", response_model=schemas.Materia, tags=["Materias"])
async def update_materia(
    materia_id: int,
    nombre: Annotated[str, Form(description="Nombre de la materia")] = None,
    creditos: Annotated[int, Form(description="Número de créditos")] = None,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(admin_required)
):
    """
    Actualizar información de una materia existente (solo administradores)
    """
    materia_data = schemas.MateriaUpdate(
        nombre=nombre if nombre else None,
        creditos=creditos if creditos else None
    )
    return materia_service.update_materia(db, materia_id, materia_data)

@app.delete("/materias/{materia_id}", response_model=schemas.ResponseMessage, tags=["Materias"])
def delete_materia(
    materia_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(admin_required)
):
    """
    Eliminar una materia del sistema (solo administradores)
    """
    return materia_service.delete_materia(db, materia_id)

# Inscripciones
@app.post("/inscripcion/{alumno_id}/{materia_id}", response_model=schemas.ResponseMessage, tags=["Inscripciones"])
def inscribir_alumno(
    alumno_id: int,
    materia_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(admin_required)
):
    """
    Inscribir un alumno en una materia específica (solo administradores)
    """
    return inscripcion_service.inscribir_alumno(db, alumno_id, materia_id)

@app.get("/inscripciones/alumno/{alumno_id}", response_model=List[schemas.Materia], tags=["Inscripciones"])
def get_materias_alumno(
    alumno_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """
    Obtener todas las materias en las que está inscrito un alumno (todos los usuarios autenticados)
    """
    return inscripcion_service.get_materias_alumno(db, alumno_id)

# Calificaciones
@app.post("/calificaciones/", response_model=schemas.Calificacion, tags=["Calificaciones"])
async def create_calificacion(
    alumno_id: Annotated[int, Form(description="ID del alumno")],
    materia_id: Annotated[int, Form(description="ID de la materia")],
    calificacion: Annotated[float, Form(description="Calificación (0-10)")],
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(admin_required)
):
    """
    Registrar una calificación (solo administradores)
    """
    calificacion_data = schemas.CalificacionCreate(
        alumno_id=alumno_id,
        materia_id=materia_id,
        calificacion=calificacion
    )
    return calificacion_service.create_calificacion(db, calificacion_data)

@app.get("/calificaciones/alumno/{alumno_id}", response_model=List[schemas.Calificacion], tags=["Calificaciones"])
def get_calificaciones_alumno(
    alumno_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """
    Obtener todas las calificaciones de un alumno (todos los usuarios autenticados)
    """
    return calificacion_service.get_calificaciones_alumno(db, alumno_id)

@app.get("/calificaciones/estadisticas/alumno/{alumno_id}", response_model=schemas.AlumnoStats, tags=["Estadísticas"])
def get_estadisticas_alumno(
    alumno_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """
    Obtener estadísticas de un alumno (todos los usuarios autenticados)
    """
    return calificacion_service.get_estadisticas_alumno(db, alumno_id)

# Rutas administrativas
@app.get("/admin/info", tags=["Administración"])
def get_admin_info():
    """
    Obtener información del administrador por defecto (solo para desarrollo)
    """
    return admin_service.get_admin_credentials()

@app.get("/users/me", response_model=schemas.User, tags=["Usuarios"])
async def read_users_me(current_user: schemas.User = Depends(get_current_user)):
    """
    Obtener información del usuario actual
    """
    return current_user