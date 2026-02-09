"""
FastAPI Application Entry Point

This is the main application file that initializes and configures
the FastAPI backend for AI Invoice Processing.

Run this application with:
    uvicorn app.main:app --reload

Or for production:
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        # In production, add file handler:
        # logging.FileHandler('invoice_processing.log')
    ]
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting AI Invoice Processing Backend...")
    logger.info("Application ready to accept requests")
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI Invoice Processing Backend...")


# Initialize FastAPI application
app = FastAPI(
    title="AI Invoice Processing Backend",
    description="""
    Production-ready MVP backend for extracting structured data from invoices.
    
    ## Features
    - Upload invoice PDFs or images
    - AI-powered data extraction
    - Automatic validation
    - Clean JSON responses
    
    ## Use Cases
    - Automated accounts payable processing
    - Invoice data entry automation
    - Accounting software integration
    - Document digitization workflows
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
# In production, restrict this to specific origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production: ["https://yourdomain.com"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, tags=["Invoice Processing"])


# Global exception handler for unhandled errors
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Catch-all exception handler to ensure we never return stack traces to clients.
    Always return structured error responses.
    """
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error_type": "INTERNAL_ERROR",
            "message": "An unexpected error occurred. Please try again later."
        }
    )


# Root endpoint
@app.get(
    "/",
    summary="API Root",
    description="Welcome endpoint with API information"
)
async def root():
    """
    Root endpoint providing API information and documentation links.
    """
    return {
        "service": "AI Invoice Processing Backend",
        "version": "1.0.0",
        "status": "operational",
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc"
        },
        "endpoints": {
            "upload_invoice": "POST /upload-invoice",
            "health_check": "GET /health"
        }
    }


if __name__ == "__main__":
    # For development only
    # In production, use a proper ASGI server (uvicorn, gunicorn, etc.)
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )
