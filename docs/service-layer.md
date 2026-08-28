# Service Layer

The service layer contains the business logic of the application. It acts as an intermediary between the API layer and the data access layer.

## Structure
- `src/handlers/*/service.py`: Contains service logic for each domain.

## Example
```python
def calculate_patient_age(date_of_birth):
    from datetime import date
    today = date.today()
    return today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))
```

## Best Practices
- Keep functions small and focused.
- Avoid direct database access; use managers instead.
- Write unit tests for all service functions.