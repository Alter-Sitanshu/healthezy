# API Layer

The API layer is implemented using FastAPI and serves as the entry point for all client requests. It is organized into modular route handlers for different domains.

## Structure
- `src/api.py`: Initializes the FastAPI app and includes all route handlers.
- `src/handlers/`: Contains route handlers for various domains.

## Key Files
- `src/api.py`: Main entry point for the API.
- `src/handlers/`: Directory containing route handlers.

## Example Route
```python
from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health_check():
    return {"status": "ok"}
```

## Permissions
- SUPERADMIN (all access for all routes)
- ADMIN (excluded from altering env or settings)
- MOD (all access to patient/appointments)
- SUPPORT (media/logging/audit team. EXCLUDED from sensitive endpoints)
- NORMAL (user)
- HOS (hospital admin level permissions)
- LAB (lab admin level permissions)

## Best Practices
- Use dependency injection for middlewares, database sessions or authorisation checks.
- Validate request data using Pydantic models.
- Return consistent response formats.