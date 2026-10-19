from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import rest, ws
from src.db.models import Base
from src.db.session import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize tables on startup if they don't exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Cleanup engine connections on shutdown
    await engine.dispose()


app = FastAPI(
    title="Real-Time Market Events API",
    description="API for accessing historical OHLCV data and real-time market streams.",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount modular routers
app.include_router(rest.router)
app.include_router(ws.router)


@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, str]:
    """
    Basic health check endpoint to verify the API is up and running.
    Used by Cloud Run startup and liveness probes.
    """
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=port)
