#!/usr/bin/env python3
"""
ThreatForge Development Startup Script
"""

import uvicorn
import os
import sys

if __name__ == "__main__":
    # Set default port
    port = int(os.environ.get("PORT", 8000))
    
    # Set default host
    host = os.environ.get("HOST", "0.0.0.0")
    
    print(f"🚀 Starting ThreatForge API on {host}:{port}")
    print(f"📚 API Documentation: http://{host}:{port}/docs")
    print(f"🔍 Health Check: http://{host}:{port}/health")
    print(f"🔄 Press Ctrl+C to stop")
    
    try:
        uvicorn.run(
            "app.main:app",
            host=host,
            port=port,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🛑 ThreatForge API stopped")
        sys.exit(0) 