from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from app.database import engine
from app.models import Base
from app.routers import auth, jobs, ai
from app.config import settings
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="ThreatForge API",
    description="AI-Enhanced Security Attack Simulation Platform API",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # Vue frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*"]  # Configure appropriately for production
)

# Include routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(jobs.router, prefix="/api/v1")
app.include_router(ai.router, prefix="/api/v1")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ThreatForge API",
        "version": "2.0.0",
        "features": ["authentication", "simulation_jobs", "ai_analysis", "pdf_reports"]
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to ThreatForge API - AI-Enhanced Security Platform",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/health",
        "ai_health": "/api/v1/ai/health"
    }

# Startup event
@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logging.info("ThreatForge API starting up...")
    logging.info(f"Database URL: {settings.database_url}")
    logging.info(f"Redis URL: {settings.redis_url}")
    logging.info(f"Tools Directory: {settings.tools_directory}")
    logging.info(f"AI Model Provider: {settings.ai_model_provider}")
    logging.info(f"AI Fallback Enabled: {settings.ai_fallback_enabled}")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logging.info("ThreatForge API shutting down...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 