import os
from dotenv import load_dotenv

load_dotenv()

# Prevent google-genai SDK from logging duplicate key warnings
if os.getenv("GOOGLE_API_KEY") and os.getenv("GEMINI_API_KEY"):
    os.environ["GEMINI_API_KEY_SECONDARY"] = os.environ.pop("GEMINI_API_KEY")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.session import test_db_connection
from app.api.auth import router as auth_router
from app.api.company import router as company_router
from app.api.watchlist import router as watchlist_router
from app.api.retrieval import retrieval_router
from app.api.chat import chat_router
from app.api.agent import agent_router
from app.api.memory.router import router as memory_router
from app.api.recommendation.router import router as recommendation_router
from app.api.system.router import router as system_router
from app.api.market.router import router as market_router
from app.api.news.router import router as news_router

app = FastAPI(
    title="Sentellent Stock Analyst API",
    version="0.1.0",
    description="Backend API for Sentellent Stock Analyst",
)

# Configurable CORS origins via ALLOWED_ORIGINS env var
raw_origins = os.getenv("ALLOWED_ORIGINS", "*")
allowed_origins = [o.strip() for o in raw_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if allowed_origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth_router)
app.include_router(company_router)
app.include_router(watchlist_router)
app.include_router(retrieval_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(agent_router, prefix="/api")
app.include_router(memory_router, prefix="/api")
app.include_router(recommendation_router, prefix="/api")
app.include_router(market_router)
app.include_router(news_router)
app.include_router(system_router)


@app.get("/")
@app.get("/health")
def health_check():
    """Health check endpoint for Docker & AWS ALB health probes."""
    return {"status": "healthy", "service": "sentellent-backend"}


@app.get("/ready")
def readiness_check():
    """Readiness probe for Kubernetes & AWS ECS task readiness."""
    return {"status": "ready", "service": "sentellent-backend"}


@app.get("/live")
def liveness_check():
    """Liveness probe for AWS ECS task container health."""
    return {"status": "live", "service": "sentellent-backend"}


@app.get("/db-health")
def db_health_check():
    """Database connectivity health probe."""
    return test_db_connection()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
