#!/usr/bin/env python3
"""
Launcher for MultiSportsBettingPlatform
"""

import uvicorn
import os
import sys
from src.main import create_fastapi_app

def main():
    """Main entry point."""
    print("🚀 Starting MultiSportsBettingPlatform")
    
    # Get server configuration
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    
    app = create_fastapi_app()
    
    if app:
        print(f"Server starting on {host}:{port}")
        try:
            uvicorn.run(
                app,
                host=host,
                port=port,
                reload=False,
                log_level="info"
            )
        except Exception as e:
            print(f"❌ Server failed to start: {e}")
            sys.exit(1)
    else:
        print("❌ Failed to create FastAPI app")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"💥 Unexpected error: {e}")
        sys.exit(1) 