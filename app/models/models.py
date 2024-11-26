from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, Table
from sqlalchemy.orm import relationship
from .database import Base

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
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

class Alumno(Base):
    __tablename__ = "alumnos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    apellido = Column(String)
    matricula = Column(String, unique=True)
    email = Column(String, unique=True)
    materias = relationship("Materia", secondary=alumno_materia, back_populates="alumnos")
    calificaciones = relationship("Calificacion", back_populates="alumno")

class Materia(Base):
    __tablename__ = "materias"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    codigo = Column(String, unique=True)
    creditos = Column(Integer)
    alumnos = relationship("Alumno", secondary=alumno_materia, back_populates="materias")
    calificaciones = relationship("Calificacion", back_populates="materia")

class Calificacion(Base):
    __tablename__ = "calificaciones"

    id = Column(Integer, primary_key=True, index=True)
    alumno_id = Column(Integer, ForeignKey("alumnos.id"))
    materia_id = Column(Integer, ForeignKey("materias.id"))
    calificacion = Column(Float)
    alumno = relationship("Alumno", back_populates="calificaciones")
    materia = relationship("Materia", back_populates="calificaciones")