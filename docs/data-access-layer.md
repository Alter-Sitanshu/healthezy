# Data Access Layer

The data access layer is responsible for interacting with the database. It uses SQLAlchemy ORM for database operations.

## Structure
- `src/database/models/`: Contains database models.
- `src/database/managers/`: Contains manager classes for database operations.

## Example Manager
```python
from sqlalchemy.orm import Session
from sqlalchemy import select
from .models.users import User

class UserManager:
    def __init__(self, session: Session):
        self.session = session

    def get_user_by_id(self, user_id: int):
        return self.session.scalar(select(User).where(User.id == user_id))
```

## Best Practices
- Use `load_only` and `joinedload` to optimize queries.
- Handle exceptions gracefully.
- Write unit tests for all manager methods.