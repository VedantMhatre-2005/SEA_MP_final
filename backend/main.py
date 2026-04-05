"""
main.py - ASPRAMS FastAPI Application Entry Point.

Starts the API server, configures CORS, registers routers,
and sets up logging.
"""

import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.settings import ALLOWED_ORIGINS
from db.mongo import init_indexes
from routes import analyze, auth, health, history


# ─── Logging ─────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


# ─── Lifespan ─────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle hooks."""
    logger.info("🚀 ASPRAMS API starting up...")
    init_indexes()
    yield
    logger.info("🛑 ASPRAMS API shutting down.")


# ─── App ──────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="ASPRAMS API",
    description=(
        "Agent-Based Software Project Risk Assessment and Mitigation System — "
        "Multi-agent negotiation engine powered by Google Gemini."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# ─── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routers ──────────────────────────────────────────────────────────────────
app.include_router(health.router, tags=["System"])
app.include_router(auth.router, tags=["Auth"])
app.include_router(analyze.router, tags=["Simulation"])
app.include_router(history.router, tags=["History"])


# ─── Root ─────────────────────────────────────────────────────────────────────
@app.get("/", tags=["System"], summary="API root")
async def root():
    return {
        "message": "Welcome to ASPRAMS API",
        "docs": "/docs",
        "health": "/health",
    }


# ─── Dev server entry point ─────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
