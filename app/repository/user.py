from fastapi import Depends, status, HTTPException, APIRouter
from .. import models, schemas
from ..database import get_db
from sqlalchemy.orm import Session
from .security.hashing import Hash

router = APIRouter(prefix="/user", tags=["user"])


def create_user(request: schemas.User, db: Session = Depends(get_db)):
    hashedPassword = Hash.get_password_hash(request.password)
    new_user = models.User(email=request.email, password=hashedPassword)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def get_user_email(email: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid credentials"
        )
    return user
