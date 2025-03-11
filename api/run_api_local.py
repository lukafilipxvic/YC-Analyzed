#!/usr/bin/env python3
"""
Run the YC Vault API server
"""
import uvicorn
import os

if __name__ == "__main__":
    # Set environment to development when running locally
    print("Starting YC Vault API server in development mode...")
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True) 