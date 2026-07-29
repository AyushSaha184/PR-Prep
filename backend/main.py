"""FastAPI main application entry point for PR Prep."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.health import router as health_router
from backend.core.config import get_settings
from backend.observability.logging import setup_logger

logger = setup_logger("pr_prep.main")
settings = get_settings()

app = FastAPI(
    title="PR Prep API",
    description="Selective Automated Pull-Request Reviewer Backend",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)


@app.on_event("startup")
async def startup_event() -> None:
    logger.info(f"PR Prep backend starting in environment: {settings.ENVIRONMENT}")
