from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# utility imports
from contextlib import asynccontextmanager
from .settings import Settings, get_settings

# Router objects for services
from .auth.routes import router as auth_router
from .handlers.users.routes import router as user_router

# Global consts
settings: Settings = get_settings()

# init application object
@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    print(f"[{settings.environment}]Server Started...")
    yield
    # shutdown
    print("Server shudown")

app = FastAPI(
    debug=True,
    title="healthezy",
    summary='''
        Healthezy backend API endpoint server
    ''',
    version="0.1.0",
    root_path="/api/v1",
    docs_url="/docs",
    lifespan=lifespan,
)
# Add CORS support
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: change this to domain later
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
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
    tags=["Users"]
)

