"""FastAPI main application entry point for PR Prep."""
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.economics_router import router as economics_router
from backend.api.governance_router import router as governance_router
from backend.api.health import router as health_router
from backend.api.hitl_router import router as hitl_router
from backend.api.queue import router as queue_router
from backend.api.reviews import router as reviews_router
from backend.api.traces import router as traces_router
from backend.core.config import get_settings
from backend.observability.logging import setup_logger
from backend.webhook_receiver.router import router as webhook_router

logger = setup_logger("pr_prep.main")
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info(f"PR Prep backend starting in environment: {settings.ENVIRONMENT}")
    yield
    logger.info("PR Prep backend shutting down cleanly.")


app = FastAPI(
    title="PR Prep API",
    description="Selective Automated Pull-Request Reviewer Backend",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(webhook_router)
app.include_router(reviews_router)
app.include_router(hitl_router)
app.include_router(economics_router)
app.include_router(queue_router)
app.include_router(traces_router)
app.include_router(governance_router)
