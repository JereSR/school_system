# config.py
import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = 'esta_es_una_clave_secreta_super_segura'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'school.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
