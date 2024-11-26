from pydantic import BaseModel
from typing import List, Optional

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True

class AlumnoBase(BaseModel):
    nombre: str
    apellido: str
    matricula: str
    email: str

class AlumnoCreate(AlumnoBase):
    pass

class Alumno(AlumnoBase):
    id: int
    
    class Config:
        from_attributes = True

class MateriaBase(BaseModel):
    nombre: str
    codigo: str
    creditos: int

class MateriaCreate(MateriaBase):
    pass

class Materia(MateriaBase):
    id: int

    class Config:
        from_attributes = True

class CalificacionBase(BaseModel):
    alumno_id: int
    materia_id: int
    calificacion: float

class CalificacionCreate(CalificacionBase):
    pass

class Calificacion(CalificacionBase):
    id: int

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None