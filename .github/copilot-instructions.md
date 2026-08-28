# AI Coding Agent Instructions for Healthezy

## Project Overview
Healthezy is a healthcare management system with a modular architecture. It includes components for managing users, patients, hospitals, labs, and appointments. The system uses FastAPI for the backend, SQLAlchemy for database interactions, and Celery for background tasks.

### Key Components
- **API Layer**: Defined in `src/api.py`, routes are modularized under `src/handlers/`.
- **Database Layer**: Models are in `src/database/models/`, and managers for database operations are in `src/database/managers/`.
- **Caching**: Redis is used for caching, with utilities in `src/cache.py`.
- **Background Tasks**: Celery tasks are defined in `src/tasks.py`.
- **Migrations**: Managed with Alembic, migration scripts are in `src/migrations/`.

## Developer Workflows
### Running the Application
1. Start the FastAPI server:
   ```bash
   uvicorn src.main:app --reload
   ```
2. Run Celery workers:
   ```bash
   celery -A src.tasks.celery_app worker --loglevel=info
   ```
3. Start Redis (required for caching and Celery):
   ```bash
   redis-server
   ```

### Database Migrations
1. Create a new migration:
   ```bash
   alembic revision --autogenerate -m "Migration message"
   ```
2. Apply migrations:
   ```bash
   alembic upgrade head
   ```

### Testing
- Use `pytest` for running tests:
  ```bash
  pytest
  ```

## Project-Specific Conventions
1. **Database Managers**:
   - Use `BaseDatabase` in `src/database/managers/manager.py` for common CRUD operations.
   - Optimize queries with `load_only` and `joinedload` to reduce data fetching overhead.
2. **Response Models**:
   - Always return Pydantic models (e.g., `UserResponse`, `PatientResponse`) for API responses.
3. **Error Handling**:
   - Raise `ManagerException` for database-related errors.

## Integration Points
- **Redis**: Used for caching and as a Celery broker.
- **Alembic**: For database schema migrations.
- **Pydantic**: For request validation and response serialization.

## Examples
### Adding a New Manager
1. Create a new file in `src/database/managers/`.
2. Inherit from `BaseDatabase` and implement methods:
   ```python
   from .manager import BaseDatabase
   from ..models.example import ExampleModel

   class ExampleManager(BaseDatabase):
       def get_example(self, id: int):
           return self.get_one(select(ExampleModel).where(ExampleModel.id == id))
   ```

### Adding a New API Route
1. Add a new route in the appropriate handler file under `src/handlers/`.
2. Use dependency injection for database sessions:
   ```python
   from fastapi import APIRouter, Depends
   from ..database.sessions import open_session

   router = APIRouter()

   @router.get("/example")
   async def get_example():
       async with open_session() as session:
           # Perform database operations
           pass
   ```