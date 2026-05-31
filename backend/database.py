import os

from sqlalchemy import ForeignKey, String, create_engine
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    sessionmaker,
)

DB_HOST = os.getenv("DB_HOST", "localhost")

DATABASE_URL = f"postgresql+psycopg2://svgv:svgv@{DB_HOST}:5432/postgres"


# postgresql+psycopg://user:password@host:port/dbname

engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False)


def run_database_operations():
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as session:
        new_user = User(username="johndoe", email="john@example.com")

        session.add(new_user)
        session.commit()
        print("Successfully created a new record inside PostgreSQL 17!")


if __name__ == "__main__":
    run_database_operations()
