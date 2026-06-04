from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Replace with your actual PostgreSQL credentials
    DATABASE_URL: str = "postgresql://svgv:svgv@database:5432/postgres"

    ALGORITHM: str = "HS256"

    class Config:
        env_file = ".env"


settings = Settings()
