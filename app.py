from flask import Flask
from flask_migrate import Migrate
from config import Config
from flask_sqlalchemy import SQLAlchemy

# Crear la app
app = Flask(__name__)
app.config.from_object(Config)

# Inicializar SQLAlchemy usando la app aquí
db = SQLAlchemy(app)

# Inicializar Migraciones (después de crear app y db)
migrate = Migrate(app, db)

# Importar modelos y rutas después de crear db para evitar import circular
from models import Usuario
from routes import main_routes

# Registrar rutas
app.register_blueprint(main_routes, url_prefix='/')

# Crear la base de datos y admin
with app.app_context():
    db.create_all()  # Crea tablas si no existen

    # Crear usuario admin si no existe
    admin = Usuario.query.filter_by(email='admin@school.com').first()
    if not admin:
        new_admin = Usuario(
            nombre='Administrador',
            apellido='Principal',
            email='admin@school.com',
            rango=4  # Director
        )
        new_admin.set_password('admin123')
        db.session.add(new_admin)
        db.session.commit()
        print("✅ Usuario admin creado: admin@school.com / admin123")

if __name__ == '__main__':
    app.run(debug=True)
