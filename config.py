from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    DATABASE = os.getenv('DATABASE')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE')

class DevelopmentConfigLocal(DevelopmentConfig):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'development_local': DevelopmentConfigLocal
}