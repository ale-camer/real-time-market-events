from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import rest, ws

app = FastAPI(
    title="Real-Time Market Events API",
    description="API for accessing historical OHLCV data and real-time market streams.",
    version="0.1.0",
)

# Configure CORS (Cross-Origin Resource Sharing)
# Critical to allow frontend web applications (like React or Vue) to consume this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Security Note: Change to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount our modular routers
app.include_router(rest.router)
app.include_router(ws.router)


@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, str]:
    """
    Basic health check endpoint to verify the API is up and running.
    Used by orchestrators like Kubernetes or Docker Compose.
    """
    return {"status": "healthy"}
