from sqlalchemy.orm import Session
from app.models.models import User, RoleEnum
from app.services import password_service
from app import schemas
from fastapi import HTTPException

ADMIN_EMAIL = "admin@school.com"
ADMIN_PASSWORD = "admin123"

def create_admin(db: Session) -> schemas.User:
    """
    Crea el usuario administrador si no existe
    """
    admin = db.query(User).filter(User.email == ADMIN_EMAIL).first()
    if not admin:
        hashed_password = password_service.get_password_hash(ADMIN_PASSWORD)
        admin = User(
            email=ADMIN_EMAIL,
            hashed_password=hashed_password,
            is_active=True,
            role=RoleEnum.ADMIN
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
    return schemas.User.from_orm(admin)

def get_admin_credentials():
    """
    Retorna las credenciales del administrador
    """
    return {
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    }