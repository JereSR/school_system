from app import db, app, Usuario
from werkzeug.security import generate_password_hash

with app.app_context():
    # Eliminar todas las tablas viejas
    db.drop_all()
    
    # Crear todas las tablas nuevas
    db.create_all()

    # Crear el usuario admin
    admin = Usuario(
        nombre="Administrador",
        apellido="Principal",
        email="admin@school.com",
        password_hash=generate_password_hash("tu_password_aqui"),
        rango=4
    )

    db.session.add(admin)
    db.session.commit()

    print("✅ Tablas recreadas y admin creado")
