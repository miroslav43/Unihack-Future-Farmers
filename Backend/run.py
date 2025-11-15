#!/usr/bin/env python3
"""Quick start script for Backend"""
import uvicorn

if __name__ == "__main__":
    print("[*] Starting Farmer Assessment Backend...")
    print("[*] API Docs: http://localhost:8000/api/docs")
    print("[*] ReDoc: http://localhost:8000/api/redoc")
    print("")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
