from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    db_url: str = "postgresql://geo:geo@localhost:5432/geo"
    redis_url: str = "redis://localhost:6379/0"
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_hours: int = 24
    production: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
