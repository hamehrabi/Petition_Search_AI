"""
Configuration settings for the petition search API.
Uses environment variables for sensitive data and deployment flexibility.

In production, these would come from environment variables or a secrets manager.

Author: Junior Developer
"""

import os
from pathlib import Path
from typing import Optional


class Settings:
    """
    Application settings loaded from environment variables.
    
    This approach allows us to:
    - Keep secrets out of code
    - Change settings without modifying code
    - Use different settings for dev/staging/production
    """
    
    def __init__(self):
        """
        Initialize settings from environment variables with sensible defaults.
        """
        # API Settings
        self.API_TITLE = os.getenv('API_TITLE', 'AI Petition Search API')
        self.API_VERSION = os.getenv('API_VERSION', '1.0.0')
        self.DEBUG_MODE = os.getenv('DEBUG_MODE', 'True').lower() == 'true'
        
        # Server Settings
        self.HOST = os.getenv('API_HOST', '0.0.0.0')
        self.PORT = int(os.getenv('API_PORT', '8000'))
        
        # File Paths
        self.BASE_DIR = Path(__file__).parent.parent
        self.DATA_DIR = self.BASE_DIR / 'data'
        self.CSV_PATH = os.getenv(
            'PETITIONS_CSV_PATH',
            str(self.DATA_DIR / 'petitions.csv')
        )
        self.EMBEDDINGS_CACHE_PATH = os.getenv(
            'EMBEDDINGS_CACHE_PATH',
            str(self.DATA_DIR / 'embeddings_cache.pkl')
        )
        
        # Model Settings
        # Using a lightweight model that's good for this task
        self.MODEL_NAME = os.getenv(
            'SENTENCE_TRANSFORMER_MODEL',
            'paraphrase-multilingual-MiniLM-L12-v2'
        )
        
        # Search Settings
        self.DEFAULT_SEARCH_LIMIT = int(os.getenv('DEFAULT_SEARCH_LIMIT', '10'))
        self.MAX_SEARCH_LIMIT = int(os.getenv('MAX_SEARCH_LIMIT', '50'))
        self.MIN_SIMILARITY_SCORE = float(os.getenv('MIN_SIMILARITY_SCORE', '0.1'))
        
        # Security Settings
        self.ALLOWED_ORIGINS = os.getenv(
            'ALLOWED_ORIGINS',
            '*'  # In production, set to specific domains
        ).split(',')
        self.RATE_LIMIT_PER_HOUR = int(os.getenv('RATE_LIMIT_PER_HOUR', '100'))
        self.MAX_QUERY_LENGTH = int(os.getenv('MAX_QUERY_LENGTH', '500'))
        
        # Ensure data directory exists
        self.DATA_DIR.mkdir(exist_ok=True)
    
    def get_log_level(self) -> str:
        """
        Get logging level based on debug mode.
        """
        return 'DEBUG' if self.DEBUG_MODE else 'INFO'
    
    def get_database_url(self) -> Optional[str]:
        """
        Get database URL if we were using a database.
        For this prototype, we're using CSV files, but in production
        we might use PostgreSQL or similar.
        """
        return os.getenv('DATABASE_URL', None)
    
    def is_production(self) -> bool:
        """
        Check if we're running in production environment.
        """
        return os.getenv('ENVIRONMENT', 'development').lower() == 'production'
    
    def validate(self):
        """
        Validate that all required settings are present and valid.
        Helps catch configuration errors early.
        """
        errors = []
        
        # Check if CSV path exists or can be created
        csv_path = Path(self.CSV_PATH)
        if not csv_path.parent.exists():
            errors.append(f"CSV directory does not exist: {csv_path.parent}")
        
        # Check model name is valid
        valid_models = [
            'paraphrase-multilingual-MiniLM-L12-v2',
            'all-MiniLM-L6-v2',
            'all-mpnet-base-v2',
            'paraphrase-MiniLM-L6-v2'
        ]
        if self.MODEL_NAME not in valid_models:
            # Not an error, just a warning
            print(f"Warning: Using non-standard model: {self.MODEL_NAME}")
        
        # Check port is valid
        if not (1 <= self.PORT <= 65535):
            errors.append(f"Invalid port number: {self.PORT}")
        
        if errors:
            raise ValueError(f"Configuration errors: {'; '.join(errors)}")
        
        return True


# Create a singleton instance
settings = Settings()


# Configuration for different environments
class DevelopmentConfig:
    """Development environment settings."""
    DEBUG = True
    RELOAD = True
    LOG_LEVEL = "debug"


class ProductionConfig:
    """Production environment settings."""
    DEBUG = False
    RELOAD = False
    LOG_LEVEL = "info"
    # In production, we'd enable these:
    # USE_HTTPS = True
    # ENABLE_RATE_LIMITING = True
    # USE_CACHE = True


class TestingConfig:
    """Testing environment settings."""
    DEBUG = True
    TESTING = True
    CSV_PATH = "test_petitions.csv"


def get_config():
    """
    Get configuration based on environment.
    """
    env = os.getenv('ENVIRONMENT', 'development').lower()
    
    configs = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig
    }
    
    return configs.get(env, DevelopmentConfig)
