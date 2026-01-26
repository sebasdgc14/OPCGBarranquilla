from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    UniqueConstraint,
    CheckConstraint,
    Boolean,
)
from .database import Base
from datetime import datetime, timezone
from sqlalchemy.orm import relationship


class Cards(Base):
    __tablename__ = "Cards"
    """
    Card model for database
    """
    db_id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # ---- Set info ----
    set_type = Column(String, index=True)  # "main", "starter", "extra", "best", "other"

    unique_id = Column(String)  # Unique identifier for the art
    unique_img_link = Column(String)  # Image link to specific art
    print_set = Column(String)  # Print set, different to card_id sometimes

    card_id = Column(String)  # Unique identifier for the card OP01-001, ST02-002, etc.
    rarity = Column(String)  # C, UC, R, SR, SEC, SP, TR, L
    name = Column(String)  # Name of the card
    card_type = Column(
        String
    )  # Straw Hat Crew / Marine / Warlord / Pirate / Revolutionary
    color = Column(String)  # Red, Green, Blue, Purple, Black, Yellow or combination A/B
    block = Column(String)  # Card block for rotation
    attribute = Column(String)  # STR, SPECIAL, STRIKE, SLASH, etc
    power = Column(String)  # Card power
    cost = Column(String)  # DON!! cost
    counter = Column(String)  # Counter value
    effect = Column(String)  # Text description of the effect

    # RELATIONSHIPS
    deck_cards = relationship(
        "DeckCards",
        back_populates="card",
    )  # Adding relationship to be able to find decks that contain a specific card for selling purposes


class User(Base):
    """
    email: for login purposes \n
    password: to be hashed
    """

    __tablename__ = "Users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String)
    password = Column(String)

    # RELATIONSHIPS
    decks = relationship(
        "Decks", back_populates="user", cascade="all, delete-orphan"
    )  # Adding the relationship so a User can have decks


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


class DeckCards(Base):
    __tablename__ = "DeckCards"
    """
    Association table between Decks and Cards

    Each row represents a card added to a specific deck.
    """

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # ---- Relations ----
    deck_id = Column(
        Integer, ForeignKey("Decks.id", ondelete="CASCADE"), index=True, nullable=False
    )  # The deck to which it belongs
    card_db_unique_id = Column(
        Integer, ForeignKey("Cards.db_id"), index=True, nullable=False
    )  # The card added

    quantity = Column(
        Integer, nullable=False, default=1
    )  # Number of copies in the deck
    added_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )  # Default time ordering

    # RELATIONSHIPS
    deck = relationship(
        "Decks", back_populates="deck_cards"
    )  # Adding relationship so that cards can belong to a deck
    card = relationship(
        "Cards", back_populates="deck_cards"
    )  # Adding relationship so that we obtain cards from the db

    __table_args__ = (
        UniqueConstraint("deck_id", "card_db_unique_id", name="uq_deck_card"),
        CheckConstraint("quantity>0", name="ck_deckcards_quantity_positive"),
    )  # Any unique card to be only once, and quantity to be at least 1
