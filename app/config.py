from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database Configuration
    database_url: str = "sqlite:///./threatforge.db"
    postgres_url: Optional[str] = None
    
    # JWT Configuration
    secret_key: str = "your-secret-key-here-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # Redis Configuration
    redis_url: str = "redis://localhost:6379"
    
    # Auth0 Configuration
    auth0_domain: Optional[str] = None
    auth0_audience: Optional[str] = None
    
    # AWS S3 Configuration
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_region: str = "us-east-1"
    s3_bucket_name: str = "threatforge-reports"
    
    # Security Tools Configuration
    tools_directory: str = "./security_tools"
    
    # AI/ML Configuration
    groq_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    ai_model_provider: str = "groq"  # groq, openai, or local
    ai_fallback_enabled: bool = True
    ai_cost_limit_per_job: float = 0.01  # Maximum cost per job in USD
    ai_model_name: str = "llama3-8b-8192"  # Default Groq model
    ai_max_tokens: int = 4000
    ai_temperature: float = 0.1
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings() 