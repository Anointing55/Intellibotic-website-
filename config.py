import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'default_secret_key'  # Secret key for session management
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///site.db'  # Database URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Disable modification tracking for performance
