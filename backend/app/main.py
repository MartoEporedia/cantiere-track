"""
Main FastAPI application entry point
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from .core.config import settings
from .core.database import engine, Base
from .routers import auth, employees, sites, attendance, reports

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address, enabled=settings.RATE_LIMIT_ENABLED)

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(employees.router, prefix="/api/employees", tags=["employees"])
app.include_router(sites.router, prefix="/api/sites", tags=["sites"])
app.include_router(attendance.router, prefix="/api/attendance", tags=["attendance"])
app.include_router(reports.router, prefix="/api/reports", tags=["reports"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "CantiereTrack API",
        "version": settings.APP_VERSION,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """
    Enhanced health check endpoint for monitoring

    Returns application status, database connectivity, and version info
    """
    from .core.database import SessionLocal
    from datetime import datetime
    import psutil
    import os

    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }

    # Check database connectivity
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        health_status["database"] = "connected"
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["database"] = f"disconnected: {str(e)}"

    # Add system metrics if available
    try:
        health_status["system"] = {
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent
        }
    except:
        # psutil might not be available, skip system metrics
        pass

    return health_status
