# Project Overview

Healthezy is a modular healthcare management system designed to handle various aspects of healthcare operations, including user management, patient records, hospital administration, lab operations, and appointment scheduling. The backend is built using FastAPI, SQLAlchemy, and Celery, ensuring scalability and maintainability.

## Key Features
- **User Management**: Handles authentication, roles, and permissions.
- **Patient Records**: Stores and manages patient data securely.
- **Hospital Administration**: Manages hospital staff, departments, and facilities.
- **Lab Operations**: Supports lab tests and applications.
- **Appointment Scheduling**: Enables efficient scheduling and management of appointments.

## Architecture
The system follows a layered architecture:
- **API Layer**: Handles HTTP requests and responses.
- **Service Layer**: Contains business logic.
- **Data Access Layer**: Manages database interactions.
- **Background Tasks**: Handles asynchronous operations using Celery.

## Tech Stack
- **Framework**: FastAPI
- **Database**: PostgreSQL/MySQL with SQLAlchemy ORM
- **Caching**: Redis
- **Testing**: Pytest