from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status
from models import Decks, DeckCards


def create_deck(user_id: int, name: str, is_wishlist: bool, db: Session):
    """
    Create a deck for a user

    Docstring for create_deck

    :param user_id: Description
    :type user_id: int
    :param name: Description
    :type name: str
    :param is_wishlist: Description
    :type is_wishlist: bool
    :param db: Description
    :type db: Session
    """
    deck = Decks(
        user_id=user_id,
        name=name,
        is_wishlist=is_wishlist,
    )
    db.add(deck)
    db.commit()
    db.refresh(deck)
    return deck


def get_deck_with_cards(deck_id: int, db: Session):
    """
    Get a deck with all its cards

    Docstring for get_deck_with_cards

    :param deck_id: Description
    :type deck_id: int
    :param db: Description
    :type db: Session
    """
    deck = (
        db.query(Decks)
        .options(joinedload(Decks.deck_cards).joinedload(DeckCards.card))
        .filter(Decks.id == deck_id)
        .first()
    )

    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")

    return deck


def add_card_to_user_deck(
    deck_id: int, card_id: int, quantity: int, user_id: int, db: Session
):
    """
    Add a card to a user's deck.
    Only the deck owner may modify it.
    """

    deck = db.query(Decks).filter(Decks.id == deck_id).first()

    if not deck:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deck not found",
        )

    if deck.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this deck",
        )

    deck_card = (
        db.query(DeckCards)
        .filter(
            DeckCards.deck_id == deck_id,
            DeckCards.card_db_unique_id == card_id,
        )
        .first()
    )

    if deck_card:
        deck_card.quantity += quantity
    else:
        deck_card = DeckCards(
            deck_id=deck_id,
            card_db_unique_id=card_id,
            quantity=quantity,
        )
        db.add(deck_card)

    db.commit()
    db.refresh(deck_card)
    return deck_card


def get_user_deck_details(
    deck_id: int,
    user_id: int,
    db: Session,
):
    """
    Return a deck with cards if and only if it belongs to the user.
    """

    deck = (
        db.query(Decks)
        .options(joinedload(Decks.deck_cards).joinedload(DeckCards.card))
        .filter(Decks.id == deck_id)
        .first()
    )

    if not deck:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deck not found",
        )

    if deck.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this deck",
        )

    return deck
