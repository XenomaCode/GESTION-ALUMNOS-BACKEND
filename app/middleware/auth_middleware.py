from fastapi import Depends, HTTPException, status
from app.models.models import User, RoleEnum
from app import schemas
from app.services.auth_service import get_user_by_email
from typing import Annotated

async def admin_required(current_user: schemas.User) -> schemas.User:
    """
    Verifica que el usuario actual sea un administrador
    """
    if current_user.role != RoleEnum.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de administrador para esta operación"
        )
    return current_user