import logging
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.config import settings, BASE_DIR
from app.database import init_schema, close_driver, check_connection
from app.routes import api_router

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("digital_legacy")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    Handles database connection verification, schema initialization, and pool closing.
    """
    logger.info(f"Starting {settings.PROJECT_NAME}...")
    try:
        status = check_connection()
        if status.get("connected"):
            logger.info(f"Connected to Neo4j at {settings.NEO4J_URI}. Initializing schema constraints...")
            init_schema()
        else:
            logger.warning(
                f"Neo4j is currently unreachable at {settings.NEO4J_URI}. "
                "The backend is operational. Once Neo4j is started, queries will automatically execute."
            )
    except Exception as e:
        logger.warning(f"Startup database check warning: {e}")

    yield

    logger.info("Shutting down application...")
    close_driver()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.PROJECT_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routes
app.include_router(api_router)

# Mount static folder
static_dir = BASE_DIR / "static"
if not static_dir.exists():
    static_dir.mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

@app.get("/", include_in_schema=False)
async def serve_home():
    """Serve the single-page application frontend."""
    index_file = static_dir / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {
        "project": settings.PROJECT_NAME,
        "message": "Frontend static/index.html is being initialized. Access API documentation at /docs."
    }
