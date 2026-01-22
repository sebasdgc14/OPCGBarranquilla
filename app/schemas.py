from pydantic import BaseModel


# class Card(BaseModel):
#     """
#     Card schema
#     """

#     unique_id: str  # Unique identifier for the art
#     unique_img_link: str  # Image link to specific art
#     print_set: str  # Print set, different to card_id sometimes

#     id: str  # Unique identifier for the card OP01-001, ST02-002, etc.
#     rarity: str  # C, UC, R, SR, SEC, SP, TR, L
#     name: str  # Name of the card
#     card_type: str  # Straw Hat Crew / Marine / Warlord / Pirate / Revolutionary
#     color: str  # Red, Green, Blue, Purple, Black, Yellow or combination A/B
#     block: str  # Card block for rotation
#     attribute: str  # STR, SPECIAL, STRIKE, SLASH, etc
#     power: str  # Card power
#     cost: str  # DON!! cost
#     counter: str  # Counter value
#     effect: str  # Text description of the effect


# Login purposes
class User(BaseModel):
    email: str
    password: str


class ShowUser(BaseModel):
    """
    Temporary to remove password showing
    """

    email: str
    password: str


class Login(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str | None = None
