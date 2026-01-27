from pydantic import BaseModel, Field
from typing import List
from datetime import datetime


# Login purposes
class User(BaseModel):
    email: str
    password: str


class ShowUser(BaseModel):
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
        from_attributes = True


class DeckOut(BaseModel):
    id: int
    name: str
    is_wishlist: bool
    created_at: datetime
    deck_cards: List[DeckCardOut]

    class Config:
        from_attributes = True
