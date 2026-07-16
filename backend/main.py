from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

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

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "API is running"}

@app.get("/api/processed-data")
async def get_processed_data():
    """Get processed outage data"""
    return {
        "message": "Data pipeline not yet implemented",
        "status": "pending"
    }

@app.get("/api/ranked-incidents")
async def get_ranked_incidents():
    """Get ranked incidents by impact score"""
    return {
        "message": "Impact scoring not yet implemented",
        "incidents": []
    }

@app.get("/api/anomalies")
async def get_anomalies():
    """Get detected anomalies"""
    return {
        "message": "Anomaly detection not yet implemented",
        "anomalies": []
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
