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

app = FastAPI(
    title="Sentellent Stock Analyst API",
    version="0.1.0",
    description="Backend API for Sentellent Stock Analyst",
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(company_router)
app.include_router(watchlist_router)
app.include_router(retrieval_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(agent_router, prefix="/api")
app.include_router(memory_router, prefix="/api")
app.include_router(recommendation_router, prefix="/api")


@app.get("/")
def health_check():
    return {"status": "running"}


@app.get("/db-health")
def db_health_check():
    return test_db_connection()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
