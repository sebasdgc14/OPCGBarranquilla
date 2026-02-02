from fastapi import Depends, status, HTTPException
import schemas
from .security import hashing
from . import user
from db.database import get_db
from sqlalchemy.orm import Session
from schemas import Token
from datetime import timedelta
from core.config import settings
from repository.security.JWTtoken import create_access_token

ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES


def authenticate_user(request: schemas.Login, db: Session = Depends(get_db)):
    user_credentials = user.get_user_email(request.username, db)
    verify_password = hashing.Hash.verify_password(
        request.password, user_credentials.password
    )
    if not verify_password:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid credentials"
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_credentials.email}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")
