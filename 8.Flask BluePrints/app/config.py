import os


class Config:
    """Base configuration class."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'
    MONGO_URI = os.environ.get('MONGO_URI') or 'mongodb://localhost:27017/flask_app'
    
    # Logging configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'logs/app.log')
    
    # Rate limiting
    RATELIMIT_STORAGE_URL = os.environ.get('RATELIMIT_STORAGE_URL', 'memory://')
    DEFAULT_RATE_LIMIT = os.environ.get('DEFAULT_RATE_LIMIT', '100/hour')

class DevelopmentConfig(Config):
    """Development configuration class."""
    DEBUG = True
    ENV = 'development'

class ProductionConfig(Config):
    """Production configuration class."""
    DEBUG = False
    ENV = 'production'

class TestingConfig(Config):
    """Testing configuration class."""
    TESTING = True
    DEBUG = True
    MONGO_URI = os.environ.get('TEST_MONGO_URI') or 'mongodb://localhost:27017/flask_app_test'

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}