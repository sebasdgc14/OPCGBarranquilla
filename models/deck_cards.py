from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    DateTime,
    UniqueConstraint,
    CheckConstraint,
)
from db.database import Base
from datetime import datetime, timezone
from sqlalchemy.orm import relationship


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
