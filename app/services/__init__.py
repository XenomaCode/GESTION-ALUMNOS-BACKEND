from .auth_service import *
from .password_service import *
from .jwt_service import *
from .alumno_service import *
from .materia_service import *
from .inscripcion_service import *
from .calificacion_service import *

__all__ = [
    # Auth services
    'authenticate_user',
    'get_user_by_email',
    'create_user',
    'get_user',
    
    # Password services
    'verify_password',
    'get_password_hash',
    
    # JWT services
    'create_access_token',
    'verify_token',
    
    # Alumno services
    'create_alumno',
    'get_alumnos',
    'get_alumno',
    'update_alumno',
    'delete_alumno',
    
    # Materia services
    'create_materia',
    'get_materias',
    'get_materia',
    'update_materia',
    'delete_materia',
    
    # Inscripcion services
    'inscribir_alumno',
    'get_materias_alumno',
    'get_alumnos_materia',
    'dar_baja_materia',
    
    # Calificacion services
    'create_calificacion',
    'get_calificaciones_alumno',
    'update_calificacion',
    'get_promedio_alumno'
]