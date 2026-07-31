from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.session import test_db_connection
from app.api.auth import router as auth_router

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


@app.get("/")
def health_check():
    return {"status": "running"}


@app.get("/db-health")
def db_health_check():
    return test_db_connection()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
