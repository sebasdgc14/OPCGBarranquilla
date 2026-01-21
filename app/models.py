from sqlalchemy import Column, Integer, String  # , ForeignKey, UniqueConstraint
from database import Base
# from sqlalchemy.orm import relationship


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


# class User(Base):
#     __tablename__ = "users"
#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String)
#     email = Column(String)
#     password = Column(String)
#     blogs = relationship("Blog", back_populates="creator")
