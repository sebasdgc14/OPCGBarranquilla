from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Boolean,
)

from db.database import Base
from datetime import datetime, timezone
from sqlalchemy.orm import relationship


class Decks(Base):
    __tablename__ = "Decks"
    """
    Deck model for database
    """

    id = Column(
        Integer, primary_key=True, index=True, autoincrement=True
    )  # Deck id, just for indexing purposes

    user_id = Column(
        Integer, ForeignKey("Users.id"), index=True, nullable=False
    )  # To determine owner of deck

    name = Column(
        String, nullable=False
    )  # Name of the deck for the user to be able to tell them apart

    is_wishlist = Column(
        Boolean,
        nullable=False,
        default=False,
        index=True,
    )  # This allows for a deck to be set as a wishlist item so that the cards in it can be searched by sellers.

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )  # Deck time creation, just for ordering purposes

    # RELATIONSHIPS
    user = relationship(
        "User", back_populates="decks"
    )  # Adding the relationship so a deck can belong to a user
    deck_cards = relationship(
        "DeckCards", back_populates="deck", cascade="all, delete-orphan"
    )  # Adding the relationshio so that a deck can have cards in it
