from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from fangen.db.models import Base


def create_db(db_path: Path) -> None:
    engine = create_engine(url=f"sqlite:///{db_path.absolute()}")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def get_session(db_path: Path) -> Session:
    engine = create_engine(url=f"sqlite:///{db_path.absolute()}")
    sm = sessionmaker(bind=engine)
    return sm()
