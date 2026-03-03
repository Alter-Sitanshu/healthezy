from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# utility imports
from contextlib import asynccontextmanager
from .settings import Settings, get_settings
from .database.sessions import ping
import logging

# Router objects for services
from .auth.routes import router as auth_router
from .handlers.admin.routes import router as admin_router
from .handlers.users.routes import router as user_router
from .handlers.doctors.routes import router as doctor_router
from .handlers.doctors.doctor_schedules.routes import router as schedule_router
from .handlers.hospitals.routes import router as hospital_router
from .handlers.hospitals.admin_routes import router as hos_admin_router
from .handlers.tenants.routes import router as tenant_router
from .handlers.doctors.doctor_schedules.exception_routes import router as schedule_exc_router
from .handlers.appointments.routes import router as appointment_router
from .handlers.patients.routes import router as patient_router
from .handlers.labs.routes import router as labs_router


# Global consts
settings: Settings = get_settings()

# logger initiation
logger = logging.getLogger(__name__)
logger.setLevel(settings.log_level)
file_handler = logging.FileHandler(filename=settings.logs_file)
file_handler.setLevel(settings.log_level)
file_handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"))
logger.addHandler(file_handler)

# init application object
@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    ping() # Pinging the database to confirm healthy connection
    logger.debug("{} - Application Start up Complete".format(settings.environment))
    yield
    # shutdown
    logger.debug("Application Shutdown Completed")

app = FastAPI(
    debug=True,
    title=settings.app_name,
    summary='''
        Healthezy backend API endpoint server
    ''',
    version=settings.app_version,
    root_path="/api/v1",
    docs_url="/docs",
    lifespan=lifespan,
)
# Add CORS support
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: change this to domain later
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-TenantID"],
    expose_headers=["*"],
)

# Attach the auth router to the application
# Register them as open handlers
@app.get("/health", tags=["System"])
async def health():
    return {"status": "ok"}

app.include_router(
    auth_router,
    prefix="/auth",
    tags=["Auth"]
)

app.include_router(
    user_router,
    prefix="/users",
    tags=["User"]
)

app.include_router(
    doctor_router,
    prefix="/doctors",
    tags=["Doctor"]
)

app.include_router(
    router=schedule_router,
    prefix="/schedules",
    tags=["Doctor Schedule"]
)

app.include_router(
    router=appointment_router,
    prefix="/appoinments",
    tags=["Appointment"]
)

app.include_router(
    router=patient_router,
    prefix="/patients",
    tags=["Patient"]
)

app.include_router(
    router=schedule_exc_router,
    prefix="/schedule_exceptions",
    tags=["Doctor Schedule Exception"]
)

app.include_router(
    router=hospital_router,
    prefix="/hospitals",
    tags=["Hospital"]
)

app.include_router(
    router=hos_admin_router,
    prefix="/hospital_admin",
    tags=["Hospital Admin"]
)

app.include_router(
    router=admin_router,
    prefix="/admin",
    tags=["Admin"]
)

app.include_router(
    router=labs_router,
    prefix="/labs",
    tags=["Labs"]
)

app.include_router(
    router=tenant_router,
    prefix="/tenants",
    tags=["Tenant"],
    deprecated=True
)
