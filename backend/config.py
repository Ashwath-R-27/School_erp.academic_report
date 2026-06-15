from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # IMPORTANT: never use default/weak creds in production. Set via .env or env var.
    # The default below is ONLY for local docker-compose with matching defaults.
    DATABASE_URL: str = "postgresql://svgv:svgv_insecure_default_change_me@database:5432/postgres"

    ALGORITHM: str = "HS256"

    class Config:
        env_file = ".env"


settings = Settings()
