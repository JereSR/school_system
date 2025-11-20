# config.py
import os
from urllib.parse import urlparse

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'esta_es_una_clave_secreta_super_segura')
    # Railway/Heroku/Postgres typically provides DATABASE_URL
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if DATABASE_URL:
        # SQLAlchemy prefers postgresql://
        SQLALCHEMY_DATABASE_URI = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    else:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'school.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
