#!/usr/bin/env python3
"""
Minimal FastAPI app that bypasses problematic imports
"""

import uvicorn
import os
import datetime
import json

def create_minimal_app():
    """Create a minimal FastAPI app."""
    try:
        # Import only the essential components
        from fastapi import FastAPI
        from fastapi.responses import JSONResponse
        
        app = FastAPI(
            title="MultiSportsBettingPlatform - YOLO MODE",
            description="YOLO MODE: Comprehensive betting platform with maximum confidence!",
            version="1.0.0-yolo"
        )
        
        @app.get("/")
        async def root():
            return {
                "message": "YOLO MODE: MultiSportsBettingPlatform is running!",
                "status": "success",
                "mode": "yolo_fastapi",
                "timestamp": datetime.datetime.now().isoformat()
            }
        
        @app.get("/health")
        async def health():
            return {
                "status": "healthy",
                "mode": "yolo_fastapi",
                "timestamp": datetime.datetime.now().isoformat()
            }
        
        @app.get("/api/v1/status")
        async def status():
            return {
                "status": "running",
                "mode": "yolo_fastapi",
                "timestamp": datetime.datetime.now().isoformat()
            }
        
        @app.post("/api/v1/predict")
        async def predict():
            return {
                "prediction": "YOLO MODE: Maximum confidence prediction!",
                "confidence": 0.95,
                "yolo_factor": 1.5,
                "mode": "yolo_fastapi",
                "timestamp": datetime.datetime.now().isoformat()
            }
        
        return app
        
    except Exception as e:
        print(f"❌ FastAPI creation failed: {e}")
        return None

def main():
    """Main function."""
    print("🚀 Starting Minimal FastAPI Server")
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    
    app = create_minimal_app()
    
    if app:
        print(f"✅ FastAPI app created, starting server on {host}:{port}")
        uvicorn.run(app, host=host, port=port, log_level="info")
    else:
        print("❌ Failed to create FastAPI app")

if __name__ == "__main__":
    main() 