#!/usr/bin/env python3
"""
Simple FastAPI test for Python 3.14 compatibility
"""

import uvicorn
import os

def test_fastapi():
    """Test if FastAPI works at all."""
    try:
        from fastapi import FastAPI
        
        app = FastAPI()
        
        @app.get("/")
        def read_root():
            return {"Hello": "World"}
        
        @app.get("/test")
        def test():
            return {"status": "FastAPI is working!"}
        
        print("✅ FastAPI app created successfully!")
        
        # Start server on port 8003
        uvicorn.run(app, host="0.0.0.0", port=8003, log_level="info")
        
    except Exception as e:
        print(f"❌ FastAPI test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_fastapi() 