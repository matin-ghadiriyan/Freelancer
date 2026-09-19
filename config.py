from dotenv import load_dotenv
import os

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Default to a local SQLite file inside the project root when DATABASE is unset.
DEFAULT_DATABASE = "sqlite:///" + os.path.join(BASE_DIR, "Freelancer.db")

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY') or 'dev-secret-key-change-me'
    DATABASE = os.getenv('DATABASE') or DEFAULT_DATABASE
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE') or DEFAULT_DATABASE
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    DEBUG = True

class DevelopmentConfigLocal(DevelopmentConfig):
    DEBUG = False

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'development_local': DevelopmentConfigLocal,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}