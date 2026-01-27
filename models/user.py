from sqlalchemy import (
    Column,
    Integer,
    String,
)
from db.database import Base
from sqlalchemy.orm import relationship


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
