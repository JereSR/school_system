from app import app
from models import db, Usuario

with app.app_context():
    admin = Usuario(nombre="Admin", apellido="Secreto", email="admin@test.com", rango=5)
    admin.set_password("1234")
    db.session.add(admin)
    db.session.commit()
    print("Usuario secreto creado exitosamente")
