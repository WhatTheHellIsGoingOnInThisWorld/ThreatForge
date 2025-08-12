#!/usr/bin/env python3
"""
Test script to verify ThreatForge project setup
"""

def test_imports():
    """Test if all required modules can be imported"""
    try:
        print("🔍 Testing imports...")
        
        # Test FastAPI and core dependencies
        import fastapi
        print("✅ FastAPI imported successfully")
        
        import sqlalchemy
        print("✅ SQLAlchemy imported successfully")
        
        import alembic
        print("✅ Alembic imported successfully")
        
        import passlib
        print("✅ Passlib imported successfully")
        
        import celery
        print("✅ Celery imported successfully")
        
        import redis
        print("✅ Redis imported successfully")
        
        import docker
        print("✅ Docker imported successfully")
        
        import reportlab
        print("✅ ReportLab imported successfully")
        
        # Test application modules
        from app.config import settings
        print("✅ App config imported successfully")
        
        from app.database import Base, engine
        print("✅ Database models imported successfully")
        
        from app.models import User, AttackSimulationJob, SimulationResult
        print("✅ Database models imported successfully")
        
        from app.schemas import UserCreate, AttackSimulationJobCreate
        print("✅ Pydantic schemas imported successfully")
        
        from app.auth import get_password_hash, verify_password
        print("✅ Authentication utilities imported successfully")
        
        print("\n🎉 All imports successful! Project setup is correct.")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure you have installed all dependencies:")
        print("   pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_database_connection():
    """Test database connection"""
    try:
        print("\n🔍 Testing database connection...")
        
        from app.database import engine
        from app.models import Base
        
        # Try to create tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database connection successful")
        print("✅ Tables created successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def test_configuration():
    """Test configuration loading"""
    try:
        print("\n🔍 Testing configuration...")
        
        from app.config import settings
        
        print(f"✅ Database URL: {settings.database_url}")
        print(f"✅ Redis URL: {settings.redis_url}")
        print(f"✅ Tools Directory: {settings.tools_directory}")
        print(f"✅ Secret Key: {'Set' if settings.secret_key != 'your-secret-key-here-change-in-production' else 'Default (change in production)'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 ThreatForge Project Setup Test")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_configuration,
        test_database_connection
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 40)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your ThreatForge project is ready to run.")
        print("\n🚀 To start the application:")
        print("   python start.py")
        print("\n🔄 To start Celery worker (in another terminal):")
        print("   python scripts/start_celery.py")
        print("\n📚 API Documentation will be available at:")
        print("   http://localhost:8000/docs")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 