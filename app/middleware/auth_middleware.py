from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from sqlalchemy.orm import Session
from app.models.models import User, RoleEnum
from app import schemas
from app.services import auth_service, jwt_service
from app.db.database import get_db
from typing import Optional

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

async def admin_required(
    security_scopes: SecurityScopes,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Optional[schemas.User]:
    """
    Verifica que el usuario actual sea un administrador
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se proporcionó token de autenticación",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    email = jwt_service.verify_token(token)
    user = auth_service.get_user_by_email(db, email=email)
    
    if not user or user.role != RoleEnum.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de administrador para esta operación"
        )
        
    return user