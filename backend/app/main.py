from fastapi import FastAPI

from app.api.deps import UnauthenticatedError, unauthenticated_exception_handler
from app.api.routes.auth import router as auth_router
from app.api.routes.health import router as health_router

# Create the central ASGI application that Uvicorn will serve.
app = FastAPI(title="Simulated Banking API")

# Auth dependencies raise one internal signal that maps to the stable 401 envelope.
app.add_exception_handler(UnauthenticatedError, unauthenticated_exception_handler)

# Keep every backend endpoint under /api so the frontend and API can share one origin.
app.include_router(health_router, prefix="/api")

# Authentication joins the same public namespace while retaining its own focused router module.
app.include_router(auth_router, prefix="/api")
