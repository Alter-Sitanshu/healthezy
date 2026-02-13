from contextlib import contextmanager
from typing import Iterator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import text, exc
from ..settings import get_settings
import logging

settings = get_settings()

# Load the Databse bind URL
DATABASE_URL: str = settings.database_url

# Create the SessionMaker class to create sessions
SessionLocal = sessionmaker(
    bind=create_engine(
        url=DATABASE_URL,
        echo=False, #OPTION: change when needed to debug
        pool_pre_ping=True,
    ),
    autoflush=False,
    autocommit=False,
    expire_on_commit=False
)

# logger initiation
logger = logging.getLogger(__name__)
logger.setLevel(settings.log_level)
file_handler = logging.FileHandler(filename=settings.logs_file)
file_handler.setLevel(settings.log_level)
file_handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"))
logger.addHandler(file_handler)

def create_session() -> Iterator[Session]:
    """
    :return: Database session instance
    :rtype: Iterator[Session]
    """
    session: Session = SessionLocal()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
    
@contextmanager
def open_session() -> Iterator[Session]:
    yield from create_session()

def ping() -> None:
    with open_session() as db:
        try:
            db.execute(text("SELECT 1"))
            logger.info("Database connection successful!")
        except exc.DBAPIError as err:
            logger.exception("Database connection failed: {}".format(err))