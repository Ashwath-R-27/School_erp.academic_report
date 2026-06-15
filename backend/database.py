from config import settings
from sqlmodel import Session, create_engine

engine = create_engine(settings.DATABASE_URL, echo=False)  # was True; query logging disabled for prod (minor info leak risk)


def get_session():
    with Session(engine) as session:
        yield session
