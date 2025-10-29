from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from app.core.config import settings
from app.core.logging_config import setup_logging
from app.middleware.error_handler import register_exception_handlers
from app.middleware.request_logging import RequestLoggingMiddleware, RequestContextMiddleware
from app.api.v1 import auth, companies, websites, users  

# Setup logging first
setup_logging()
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
    description="""
    # Chatbot SaaS Platform API
    
    A comprehensive SaaS platform for managing AI-powered chatbots.
    
    ## Features
    
    * **Authentication & Authorization**: JWT-based authentication with role-based access control
    * **Company Management**: Create and manage client companies with resource plans
    * **User Management**: Multi-level user hierarchy with custom permissions
    * **Website Management**: Create and manage websites with chatbot widgets
    * **Resource Allocation**: Track and manage resource usage and limits
    * **Comprehensive Logging**: Structured logging with request tracking
    * **Error Handling**: Standardized error responses with detailed information
    
    ## Authentication
    
    All endpoints (except auth endpoints) require a valid JWT token in the Authorization header:
```
    Authorization: Bearer <your_access_token>
```
    """,
    contact={
        "name": "API Support",
        "email": settings.FIRST_SUPERUSER_EMAIL,
    },
)

# ========================
# CORS Middleware
# ========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========================
# Custom Middlewares
# ========================
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RequestContextMiddleware)

# ========================
# Exception Handlers
# ========================
register_exception_handlers(app)

# ========================
# Health Check Endpoint
# ========================
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "version": settings.VERSION
    }

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "version": settings.VERSION,
        "docs_url": "/docs" if settings.ENVIRONMENT != "production" else None,
        "environment": settings.ENVIRONMENT
    }

# ========================
# API Routes
# ========================
app.include_router(
    auth.router,
    prefix=f"{settings.API_V1_STR}/auth",
    tags=["Authentication"]
)

app.include_router(
    companies.router,
    prefix=f"{settings.API_V1_STR}/companies",
    tags=["Companies"]
)


app.include_router(
    websites.router,
    prefix=f"{settings.API_V1_STR}/websites",
    tags=["Websites"]
)

app.include_router(
    users.router,
    prefix=f"{settings.API_V1_STR}/users",
    tags=["Users"]
)

# ========================
# Startup & Shutdown Events
# ========================
@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info("Application startup complete")

@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    logger.info("Application shutting down")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True if settings.ENVIRONMENT == "development" else False
    )