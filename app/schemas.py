from pydantic import BaseModel, EmailStr, Field, StringConstraints
from typing import List, Optional, Annotated
from enum import Enum

class RoleEnum(str, Enum):
    ADMIN = "admin"
    USER = "user"

# Esquemas de Usuario
class UserBase(BaseModel):
    email: EmailStr = Field(..., description="Correo electrónico del usuario")

class UserCreate(UserBase):
    password: str = Field(
        ...,
        min_length=8,
        description="Contraseña del usuario (mínimo 8 caracteres)"
    )
    role: Optional[RoleEnum] = Field(
        default=RoleEnum.USER,
        description="Rol del usuario (admin/user)"
    )

class User(UserBase):
    id: int
    is_active: bool
    role: RoleEnum

    class Config:
        from_attributes = True

# Esquemas de Alumno
class AlumnoBase(BaseModel):
    nombre: Annotated[str, StringConstraints(min_length=2, max_length=50)] = Field(..., description="Nombre del alumno")
    apellido: Annotated[str, StringConstraints(min_length=2, max_length=50)] = Field(..., description="Apellido del alumno")
    matricula: Annotated[str, StringConstraints(min_length=5, max_length=20)] = Field(..., description="Matrícula única del alumno")
    email: EmailStr = Field(..., description="Correo electrónico del alumno")

class AlumnoCreate(AlumnoBase):
    pass

class AlumnoInDB(AlumnoBase):
    id: int

    class Config:
        from_attributes = True

class Alumno(AlumnoInDB):
    calificaciones: List['Calificacion'] = []
    materias: List['Materia'] = []

# Esquemas de Materia
class MateriaBase(BaseModel):
    nombre: Annotated[str, StringConstraints(min_length=3, max_length=100)] = Field(..., description="Nombre de la materia")
    codigo: Annotated[str, StringConstraints(min_length=3, max_length=20)] = Field(..., description="Código único de la materia")
    creditos: int = Field(..., ge=1, le=10, description="Número de créditos (1-10)")

class MateriaCreate(MateriaBase):
    pass

class MateriaInDB(MateriaBase):
    id: int

    class Config:
        from_attributes = True

class Materia(MateriaInDB):
    alumnos: List[AlumnoInDB] = []
    calificaciones: List['Calificacion'] = []

# Esquemas de Calificación
class CalificacionBase(BaseModel):
    alumno_id: int = Field(..., description="ID del alumno")
    materia_id: int = Field(..., description="ID de la materia")
    calificacion: float = Field(..., ge=0.0, le=10.0, description="Calificación (0-10)")

class CalificacionCreate(CalificacionBase):
    pass

class Calificacion(CalificacionBase):
    id: int

    class Config:
        from_attributes = True

# Esquemas de Token
class Token(BaseModel):
    access_token: str
    token_type: str = Field(default="bearer")
    role: Optional[str] = None
    expires_in: int = Field(
        default=1800,
        description="Tiempo de expiración del token en segundos"
    )

class TokenData(BaseModel):
    email: Optional[EmailStr] = None
    role: Optional[RoleEnum] = None

# Esquemas de respuesta
class ResponseMessage(BaseModel):
    message: str
    status: str = Field(default="success")
    data: Optional[dict] = None

# Esquemas para estadísticas
class AlumnoStats(BaseModel):
    total_materias: int
    promedio_general: float
    creditos_cursados: int

class MateriaStats(BaseModel):
    total_alumnos: int
    promedio_grupal: float
    aprobados: int
    reprobados: int

# Update esquemas parciales
class AlumnoUpdate(BaseModel):
    nombre: Optional[Annotated[str, StringConstraints(min_length=2, max_length=50)]] = None
    apellido: Optional[Annotated[str, StringConstraints(min_length=2, max_length=50)]] = None
    email: Optional[EmailStr] = None

class MateriaUpdate(BaseModel):
    nombre: Optional[Annotated[str, StringConstraints(min_length=3, max_length=100)]] = None
    creditos: Optional[int] = Field(None, ge=1, le=10)

class CalificacionUpdate(BaseModel):
    calificacion: float = Field(..., ge=0.0, le=10.0)

# Actualizar referencias circulares
Alumno.update_forward_refs()
Materia.update_forward_refs()