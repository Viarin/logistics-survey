import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import OperationalError
from app.api import surveys
from app.core.database import engine, Base

logger = logging.getLogger(__name__)

app = FastAPI(title="Viarin Survey System")


@app.on_event("startup")
def on_startup():
    # Ensure models are imported so their tables are registered on Base.metadata.
    from app.models import survey  # noqa: F401

    try:
        Base.metadata.create_all(bind=engine)
    except OperationalError:
        # Keep startup clean when DB isn't running locally.
        logger.warning("Database is unreachable; skipping create_all() on startup.")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(surveys.router)


@app.get("/")
def health_check():
    return {"status": "running"}

