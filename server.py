"""
FastAPI application for AtlasMind backend
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import routes (we'll create these)
from routes import video, qa, notes, quiz

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    print("🚀 AtlasMind Backend Starting...")
    yield
    print("💤 AtlasMind Backend Shutting Down...")

# Create FastAPI app
app = FastAPI(
    title="AtlasMind API",
    description="AI Learning Companion Backend API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(video.router, prefix="/api/video", tags=["Video"])
app.include_router(qa.router, prefix="/api/qa", tags=["Q&A"])
app.include_router(notes.router, prefix="/api/notes", tags=["Notes"])
app.include_router(quiz.router, prefix="/api/quiz", tags=["Quiz"])

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "AtlasMind Backend",
        "version": "1.0.0"
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to AtlasMind API",
        "docs": "/docs",
        "health": "/api/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=os.getenv("SERVER_HOST", "0.0.0.0"),
        port=int(os.getenv("SERVER_PORT", 8000))
    )
