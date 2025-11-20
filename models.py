from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    apellido = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    rango = db.Column(db.Integer, nullable=False)  # 1=Profesor, 2=Preceptor, 3=Vice, 4=Secretaria , 5=Director

    solicitudes = db.relationship(
    'Solicitud',
    backref='usuario',
    foreign_keys='Solicitud.usuario_id'
)
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Alumno(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # ID automático
    nombre = db.Column(db.String(50), nullable=False)
    apellido = db.Column(db.String(50), nullable=False)
    domicilio = db.Column(db.String(100))
    email = db.Column(db.String(100))
    edad = db.Column(db.Integer)
    telefono = db.Column(db.String(20))
    grado = db.Column(db.String(10), nullable=False)
    division = db.Column(db.String(10), nullable=False)
    especialidad = db.Column(db.String(50))


class Solicitud(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	tipo = db.Column(db.String(20), nullable=False)   # 'editar', 'modificar' o 'borrar'
	motivo = db.Column(db.Text, nullable=False)
	estado = db.Column(db.String(20), nullable=False, default='pendiente')  # pendiente, aprobada, rechazada
	creado_en = db.Column(db.DateTime, default=datetime.utcnow)

	# datos nuevos en caso de solicitud de modificación (almacenados como JSON string)
	datos_nuevos = db.Column(db.Text, nullable=True)

	# quien la solicitó (profesor)
	usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
	solicitante = db.relationship('Usuario', foreign_keys=[usuario_id], backref='solicitudes_solicitadas')

	# alumno afectado
	alumno_id = db.Column(db.Integer, db.ForeignKey('alumno.id'), nullable=False)
	alumno = db.relationship('Alumno', foreign_keys=[alumno_id])

	# quien aprobó/rechazó
	aprobador_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=True)
	aprobador = db.relationship('Usuario', foreign_keys=[aprobador_id], backref='solicitudes_aprobadas')

	def __repr__(self):
		return f'<Solicitud {self.id} - {self.tipo} - {self.estado}>'
