"""
Configuration settings for the Ecommerce AI Agent
"""
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    """Application settings and configuration"""
    
    # API Configuration
    API_TITLE: str = "Ecommerce AI Agent"
    API_DESCRIPTION: str = "AI-powered ecommerce analytics with visualizations and real-time streaming" 
    API_VERSION: str = "1.0.0"
    
    # Server Configuration
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    DEBUG: bool = True
    
    # Database Configuration
    DATABASE_URL: str = "sqlite:///./data.db"
    DB_PATH: str = os.path.join(os.path.dirname(__file__), "../data.db")
    
    # LLM Configuration
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    GEMINI_URL: str = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    
    # Data Configuration
    DATA_DIR: str = os.path.join(os.path.dirname(__file__), "../data")
    
    # Visualization Configuration
    MAX_CHART_POINTS: int = 1000
    DEFAULT_CHART_WIDTH: int = 800
    DEFAULT_CHART_HEIGHT: int = 600
    
    # CORS Configuration
    ALLOWED_ORIGINS: list = ["*"]
    ALLOWED_METHODS: list = ["*"]
    ALLOWED_HEADERS: list = ["*"]

    @classmethod
    def validate(cls) -> bool:
        """Validate required settings"""
        if not cls.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is required but not set in environment variables")
        return True

# Global settings instance
settings = Settings()
