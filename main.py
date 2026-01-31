"""Main server application"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from datetime import datetime

from config import settings
from database import connect_db, disconnect_db
from routes import doctor_router, slot_router, token_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting OPD Token Allocation Engine...")
    await connect_db()
    logger.info("Application started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down OPD Token Allocation Engine...")
    await disconnect_db()
    logger.info("Application shut down successfully")


# Create FastAPI application
app = FastAPI(
    title="OPD Token Allocation Engine",
    description="Hospital OPD Token Allocation System with Dynamic Capacity Management",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests"""
    logger.info(f"{datetime.utcnow().isoformat()} - {request.method} {request.url.path}")
    response = await call_next(request)
    return response


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "OK",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "OPD Token Allocation Engine",
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "OPD Token Allocation Engine API",
        "version": "1.0.0",
        "endpoints": {
            "doctors": "/api/doctors",
            "slots": "/api/slots",
            "tokens": "/api/tokens",
            "health": "/health",
            "docs": "/docs",
        },
        "documentation": "Visit /docs for interactive API documentation",
    }


# Include routers
app.include_router(doctor_router)
app.include_router(slot_router)
app.include_router(token_router)


# 404 handler
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Handle 404 errors"""
    return JSONResponse(
        status_code=404,
        content={
            "success": False,
            "error": "Route not found",
        }
    )


# Generic exception handler
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Handle generic exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "detail": str(exc) if settings.ENVIRONMENT == "development" else "An error occurred",
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    print("""
╔═══════════════════════════════════════════════════════╗
║   OPD Token Allocation Engine                         ║
║   Server running on port {port}                       ║
║   Environment: {env}                                  ║
║   Time: {time}                                        ║
╚═══════════════════════════════════════════════════════╝
    """.format(
        port=settings.PORT,
        env=settings.ENVIRONMENT,
        time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    
    print("API Endpoints:")
    print("  - GET  /health")
    print("  - GET  /docs")
    print("  - GET  /api/doctors")
    print("  - POST /api/doctors")
    print("  - GET  /api/slots")
    print("  - POST /api/slots")
    print("  - POST /api/tokens/book")
    print("  - POST /api/tokens/walkin")
    print("  - POST /api/tokens/priority")
    print("  - POST /api/tokens/emergency")
    print("\nReady to accept requests!\n")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.ENVIRONMENT == "development",
    )
