from contextlib import contextmanager
from typing import Iterator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from ..settings import get_settings

settings = get_settings()

# Load the Databse bind URL
DATABASE_URL: str = settings.database_url

# Create the SessionMaker class to create sessions
SessionLocal = sessionmaker(
    bind=create_engine(
        url=DATABASE_URL,
        echo=False #OPTION: change when needed to debug
    ),
    autoflush=False,
    autocommit=False,
    expire_on_commit=False
)

def create_session() -> Iterator[Session]:
    """
    :return: Database session instance
    :rtype: Iterator[Session]
    """
    session: Session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        # TODO: add Logging feature
        print(e)
        # logger.error(f"session error: {e}")
        raise
    finally:
        session.close()
    
@contextmanager
def open_session() -> Iterator[Session]:
    return create_session()

