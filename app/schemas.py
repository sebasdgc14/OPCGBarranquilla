from pydantic import BaseModel, Field
from typing import List
from datetime import datetime


# Login purposes
class User(BaseModel):
    email: str
    password: str


class ShowUser(BaseModel):
    """
    Temporary to remove password showing
    """

    email: str


class Login(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str | None = None


class CreateDeck(BaseModel):
    name: str
    is_wishlist: bool = False


class AddCardToDeck(BaseModel):
    card_id: int
    quantity: int = Field(default=1, ge=1)


class DeckCardOut(BaseModel):
    card_db_unique_id: int
    quantity: int

    class Config:
        orm_mode = True


class DeckOut(BaseModel):
    id: int
    name: str
    is_wishlist: bool
    created_at: datetime

    # ✅ MATCHES ORM ATTRIBUTE NAME
    deck_cards: List[DeckCardOut]

    class Config:
        orm_mode = True
