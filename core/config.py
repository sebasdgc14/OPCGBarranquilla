import os
from dotenv import load_dotenv

load_dotenv()


def _get_required(name: str) -> str:
    value = os.getenv(name)
    if value is None or value == "":
        raise ValueError(f"Missing required environment variable: {name}")
    return value


def _get_int_required(name: str) -> int:
    value = _get_required(name)
    try:
        return int(value)
    except ValueError as exc:
        raise ValueError(f"Invalid integer for environment variable: {name}") from exc


DATABASE_URL = _get_required("DATABASE_URL")
PATH_IMAGES = os.getenv("PATH_IMAGES", "images")
PATH_DATABASE_LOCAL = os.getenv("PATH_DATABASE_LOCAL", "db")
PATH_KEYS = os.getenv("PATH_KEYS", "app/scripts/sets_ids.json")
SECRET_KEY = _get_required("SECRET_KEY")
ALGORITHM = _get_required("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = _get_int_required("ACCESS_TOKEN_EXPIRE_MINUTES")
