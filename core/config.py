from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    PATH_IMAGES: str
    PATH_DATABASE_LOCAL: str
    PATH_KEYS: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()  # instantiate settings to use throughout the application
