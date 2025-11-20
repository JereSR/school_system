from app import app
from models import db, Alumno

with app.app_context():
    # Lista de alumnos de prueba
    alumnos = [
        Alumno(nombre="Juan", apellido="Pérez", domicilio="Calle Falsa 123",
               email="juan@mail.com", edad=16, telefono="12345678", grado=4, division="A", especialidad="Informática"),
        Alumno(nombre="María", apellido="Gómez", domicilio="Av. Siempre Viva 742",
               email="maria@mail.com", edad=17, telefono="87654321", grado=4, division="B", especialidad="Electromecánica"),
        Alumno(nombre="Lucas", apellido="Ramírez",  domicilio="Calle Luna 12",
               email="lucas@mail.com", edad=16, telefono="11223344", grado=5, division="A", especialidad="Informática"),
    ]

    for alumno in alumnos:
        db.session.add(alumno)
    db.session.commit()
    print("Alumnos de prueba creados exitosamente")
