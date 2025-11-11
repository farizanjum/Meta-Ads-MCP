#!/usr/bin/env python3
"""
Standalone entry point for running the OAuth web server.
This runs separately from the MCP server.
"""
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from auth.web_server import app
from config.settings import settings
import uvicorn

if __name__ == "__main__":
    print(f"Starting Meta Ads OAuth web server on {settings.web_server_host}:{settings.web_server_port}")
    print(f"Environment: {settings.environment}")
    print(f"OAuth enabled: {settings.fb_oauth_enabled}")
    print(f"OAuth configured: {settings.is_oauth_configured}")
    
    if not settings.is_oauth_configured:
        print("\n⚠️  WARNING: OAuth is not fully configured!")
        print("   Set FB_APP_ID, FB_APP_SECRET, and FB_REDIRECT_URI to enable OAuth.")
        print("   See .env.example for details.\n")
    
    uvicorn.run(
        app,
        host=settings.web_server_host,
        port=settings.web_server_port,
        log_level=settings.log_level.lower()
    )

