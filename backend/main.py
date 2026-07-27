from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import sys
import logging
from dotenv import load_dotenv

# Setup path for imports
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(backend_dir))  # Add parent to path so we can import backend

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="NOC Outage Impact API",
    description="API for telecom outage impact prioritization system",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routers (using relative imports from backend package)
try:
    from backend.api import data, incidents, anomalies
except ImportError:
    from api import data, incidents, anomalies

# Include routers
app.include_router(data.router)
app.include_router(incidents.router)
app.include_router(anomalies.router)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "API is running", "version": "0.1.0"}

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "NOC Outage Impact API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
