from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.models import User
from app.services import password_service

def authenticate_user(db: Session, email: str, password: str):
    """
    Autentica un usuario verificando su email y contraseña
    """
    user = get_user_by_email(db, email)
    if not user:
        return False
    if not password_service.verify_password(password, user.hashed_password):
        return False
    return user

def get_user_by_email(db: Session, email: str):
    """
    Obtiene un usuario por su email
    """
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user_create):
    """
    Crea un nuevo usuario
    """
    hashed_password = password_service.get_password_hash(user_create.password)
    db_user = User(email=user_create.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user(db: Session, user_id: int):
    """
    Obtiene un usuario por su ID
    """
    return db.query(User).filter(User.id == user_id).first()