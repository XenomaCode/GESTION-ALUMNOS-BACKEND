from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, Table, Enum
from sqlalchemy.orm import relationship
from app.db.database import Base
import enum

# Definición del enum para roles
class RoleEnum(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"

# Tabla intermedia para la relación muchos a muchos entre alumnos y materias
alumno_materia = Table(
    'alumno_materia',
    Base.metadata,
    Column('alumno_id', Integer, ForeignKey('alumnos.id')),
    Column('materia_id', Integer, ForeignKey('materias.id'))
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    role = Column(Enum(RoleEnum), default=RoleEnum.USER, nullable=False)

class Alumno(Base):
    __tablename__ = "alumnos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), index=True, nullable=False)
    apellido = Column(String(50), nullable=False)
    matricula = Column(String(20), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)

    # Relaciones
    materias = relationship(
        "Materia",
        secondary=alumno_materia,
        back_populates="alumnos"
    )
    calificaciones = relationship(
        "Calificacion",
        back_populates="alumno",
        cascade="all, delete-orphan"
    )

class Materia(Base):
    __tablename__ = "materias"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), index=True, nullable=False)
    codigo = Column(String(20), unique=True, nullable=False)
    creditos = Column(Integer, nullable=False)

    # Relaciones
    alumnos = relationship(
        "Alumno",
        secondary=alumno_materia,
        back_populates="materias"
    )
    calificaciones = relationship(
        "Calificacion",
        back_populates="materia",
        cascade="all, delete-orphan"
    )

class Calificacion(Base):
    __tablename__ = "calificaciones"

    id = Column(Integer, primary_key=True, index=True)
    alumno_id = Column(Integer, ForeignKey("alumnos.id"), nullable=False)
    materia_id = Column(Integer, ForeignKey("materias.id"), nullable=False)
    calificacion = Column(Float, nullable=False)

    # Relaciones
    alumno = relationship("Alumno", back_populates="calificaciones")
    materia = relationship("Materia", back_populates="calificaciones")

    class Config:
        orm_mode = True