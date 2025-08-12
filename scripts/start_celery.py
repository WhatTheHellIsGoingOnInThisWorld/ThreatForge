#!/usr/bin/env python3
"""
Celery Worker Startup Script for ThreatForge
"""

import os
import sys
import subprocess

def start_celery_worker():
    """Start Celery worker"""
    print("🚀 Starting Celery Worker...")
    
    cmd = [
        "celery", "-A", "app.celery_app", 
        "worker", 
        "--loglevel=info",
        "--concurrency=2"
    ]
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting Celery worker: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Celery worker stopped")
        sys.exit(0)

def start_celery_beat():
    """Start Celery beat scheduler"""
    print("⏰ Starting Celery Beat Scheduler...")
    
    cmd = [
        "celery", "-A", "app.celery_app", 
        "beat", 
        "--loglevel=info"
    ]
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting Celery beat: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Celery beat stopped")
        sys.exit(0)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "beat":
        start_celery_beat()
    else:
        start_celery_worker() 