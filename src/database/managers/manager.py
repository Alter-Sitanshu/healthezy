from sqlalchemy.sql.expression import Executable
from sqlalchemy.orm import Session
from typing import Any, List

class SessionMixin:
    """Provides instance of database session."""

    def __init__(self, session: Session) -> None:
        self.session = session

class BaseDatabase(SessionMixin):
    """
    Base Data manager class responsible for
    operation of database models
    """
    def add_one(self, model: Any):
        try:
            self.session.add(model)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise ValueError(f"Error inserting into DB: {str(e)}")
    def add_all(self, models: List[Any]) -> None:
        try:
            self.session.add_all(models)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise ValueError(f"Error inserting multiple rows: {str(e)}")

    def get_one(self, select_stmt: Executable) -> Any:
        return self.session.scalar(select_stmt)

    def get_all(self, select_stmt: Executable) -> List[Any]:
        return list(self.session.scalars(select_stmt).all())
    
    def delete_one(self, model: Any) -> None:
        self.session.delete(model)
        self.session.commit()

    def execute_stmt(self, stmt: Executable) -> Any:
        res = self.session.execute(stmt)
        self.session.commit()
        return res