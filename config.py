# config.py
import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
	SECRET_KEY = os.environ.get('SECRET_KEY', 'esta_es_una_clave_secreta_super_segura')
	
	# Usar DATABASE_URL si está disponible (Railway/Heroku), si no usar SQLite local
	DATABASE_URL = os.environ.get('DATABASE_URL')
	if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
		SQLALCHEMY_DATABASE_URI = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
	elif DATABASE_URL:
		SQLALCHEMY_DATABASE_URI = DATABASE_URL
	else:
		SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'school.db')
	
	SQLALCHEMY_TRACK_MODIFICATIONS = False
