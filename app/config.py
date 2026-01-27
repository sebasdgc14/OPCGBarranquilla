import os
from dotenv import load_dotenv


load_dotenv()


def _get_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None or value == "":
        return default
    try:
        return int(value)
    except ValueError:
        return default


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
SECRET_KEY = _get_required("SECRET_KEY")
ALGORITHM = _get_required("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = _get_int_required("ACCESS_TOKEN_EXPIRE_MINUTES")
