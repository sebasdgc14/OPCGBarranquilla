from fastapi import Depends, APIRouter
from ..database import get_db
from sqlalchemy.orm import Session
from .. import schemas
from ..repository import authentication
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(prefix="/login", tags=["Authentication"])


@router.post("", response_model=schemas.Token)
def login(
    request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    return authentication.authenticate_user(request, db)
