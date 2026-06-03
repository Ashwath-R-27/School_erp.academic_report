from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Replace with your actual PostgreSQL credentials
    DATABASE_URL: str = "postgresql://svgv:svgv@localhost:5432/postgres"
    SECRET_KEY: str = "your_super_secret_jwt_key"
    ALGORITHM: str = "HS256"

    class Config:
        env_file = ".env"


settings = Settings()
