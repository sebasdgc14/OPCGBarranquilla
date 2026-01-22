from fastapi import Depends, APIRouter
from .. import schemas
from ..database import get_db
from sqlalchemy.orm import Session
from ..repository import user
from ..repository.security import oauth2

router = APIRouter(prefix="/user", tags=["User"])


@router.post("", response_model=schemas.ShowUser)
def create_user(request: schemas.User, db: Session = Depends(get_db)):
    return user.create_user(request, db)


@router.get("/collection")
def get_collection(
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(oauth2.get_current_user),
):
    return 0
