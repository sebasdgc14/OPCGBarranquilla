from pydantic import BaseModel


class Card(BaseModel):
    """
    A class to represent a card.
    """

    unique_id: str
    unique_img_link: str
    print_set: str

    id: str  # Unique identifier for the card OP01-001, ST02-002, etc.
    rarity: str  # C, UC, R, SR, SEC, SP, TR, L
    name: str  # Name of the card
    card_type: list[str]  # Straw Hat Crew / Marine / Warlord / Pirate / Revolutionary
    color: list[str]  # Red, Green, Blue, Purple, Black, Yellow or combination A/B
    effect: str  # Text description of the effect
    block: str  # Card block for rotation
    attribute: list[str]
    power: str
    cost: str
    counter: str
