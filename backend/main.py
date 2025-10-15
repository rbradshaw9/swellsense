from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from database import init_db
from routers import forecast, ai, status
from scheduler import global_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown"""
    # Startup: Initialize database
    await init_db()
    
    # Start global data ingestion scheduler (runs hourly)
    global_scheduler.start()
    
    yield
    
    # Shutdown: Stop background tasks and clean up resources
    await global_scheduler.stop()


# Create FastAPI instance
app = FastAPI(
    title="SwellSense API",
    description="AI-powered surf forecasting API that analyzes buoy, wind, and tide data",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Include routers
app.include_router(status.router)
app.include_router(forecast.router)
app.include_router(ai.router)

# Configure CORS
origins = [
    "http://localhost:3000",  # Next.js dev server
    "https://swellsense.app",  # Production domain
    "https://*.vercel.app",    # Vercel preview deployments
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Welcome route
@app.get("/")
async def welcome():
    """Welcome endpoint for SwellSense API"""
    return JSONResponse(
        content={
            "message": "Welcome to SwellSense API 🌊",
            "description": "AI-powered surf forecasting that analyzes buoy, wind, and tide data",
            "version": "1.0.0",
            "docs": "/docs"
        }
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return JSONResponse(
        content={
            "status": "healthy",
            "service": "SwellSense API"
        }
    )

# API info endpoint
@app.get("/api/info")
async def api_info():
    """API information endpoint"""
    return JSONResponse(
        content={
            "name": "SwellSense API",
            "version": "1.0.0",
            "features": [
                "Surf forecasting",
                "Buoy data analysis",
                "Wind pattern analysis",
                "Tide predictions",
                "AI-powered recommendations"
            ],
            "status": "active"
        }
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )