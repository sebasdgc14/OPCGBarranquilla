from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends
from typing import Annotated
from .. import user
from ...database import get_db
from . import JWTtoken

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="login"
)  # this is the route where the token will be fetched from


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db=Depends(get_db)):
    token_data = JWTtoken.verify_token(token)
    user_data = user.get_user_email(email=token_data.email, db=db)
    return user_data
