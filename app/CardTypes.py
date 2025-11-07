from pydantic import BaseModel


class Card(BaseModel):
    """
    A class to represent a card.
    """

    id: int  # Unique identifier for the card OP01-001, ST02-002, etc.
    rarity: str  # C, UC, R, SR, SEC, SP, TR, L
    name: str  # Name of the card
    type: str  # Straw Hat Crew / Marine / Warlord / Pirate / Revolutionary
    color: list[str]  # Red, Green, Blue, Purple, Black, Yellow or combination A/B
    effect: str | None  # Text description of the effect


class LeaderCard(Card):
    """
    A class to represent a leader card.
    """

    attribute: list[str]  # Strike, Special, Slash, Wisdom, Ranged, ?
    power: int  # Attack power


class EventCard(Card):
    """
    A class to represent an event or stage card.
    """

    cost: int  # Don!! cost to play
    trigger: str  # Effect when played from life


class CharacterCard(LeaderCard):
    """
    A class to represent a character card.
    """

    cost: int  # Don!! cost to play
    trigger: str  # Effect when played from life
    counter: int  # Counter power
