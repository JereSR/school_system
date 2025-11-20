from flask import Blueprint, render_template, redirect, url_for, request, session, flash, abort
from models import db, Usuario, Alumno, Solicitud
import pandas as pd
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import json

main_routes = Blueprint('main', __name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'xlsx', 'csv'}

# ---------- FUNCIONES AUXILIARES ----------
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ---------- LOGIN ----------
@main_routes.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password']

        usuario = Usuario.query.filter_by(email=email).first()

        if usuario and usuario.check_password(password):
            session['user_id'] = usuario.id
            session['rango'] = usuario.rango
            session['nombre'] = f"{usuario.nombre} {usuario.apellido}"
            session['correo'] = usuario.email
            flash(f"Bienvenido {usuario.nombre}!", "success")
            return redirect(url_for('main.dashboard'))
        else:
            flash('Usuario o contraseña incorrectos', 'danger')

    return render_template('login.html')


# ---------- LOGOUT ----------
@main_routes.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada correctamente', 'info')
    return redirect(url_for('main.login'))


# ---------- DASHBOARD ----------
@main_routes.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    return render_template('dashboard.html',
                           nombre=session.get('nombre'),
                           rango=session.get('rango'))


# ---------- LISTA DE ALUMNOS ----------
@main_routes.route('/alumnos')
def alumnos():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    alumnos = Alumno.query.all()
    return render_template('alumnos.html',
                           alumnos=alumnos,
                           rango=session.get('rango', 0))


# ---------- NUEVO ALUMNO ----------
@main_routes.route('/alumno/nuevo', methods=['GET', 'POST'])
def nuevo_alumno():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    if session.get('rango', 0) < 2:
        flash("No tenés permiso para crear alumnos", "warning")
        return redirect(url_for('main.alumnos'))

    if request.method == 'POST':
        grado_str = request.form.get('grado', '').strip()
        grado_num = int(grado_str[0]) if grado_str and grado_str[0].isdigit() else 0
        especialidad = request.form.get('especialidad') if grado_num >= 4 else None

        alumno = Alumno(
            nombre=request.form.get('nombre', '').strip(),
            apellido=request.form.get('apellido', '').strip(),
            domicilio=request.form.get('domicilio', '').strip(),
            email=request.form.get('email', '').strip(),
            edad=int(request.form.get('edad', 0)) if request.form.get('edad') else None,
            telefono=request.form.get('telefono', '').strip(),
            grado=grado_str,
            division=request.form.get('division', '').strip(),
            especialidad=especialidad
        )

        db.session.add(alumno)
        db.session.commit()
        flash("Alumno creado correctamente", "success")
        return redirect(url_for('main.alumnos'))

    return render_template('alumno_form.html', alumno=None)


# ---------- EDITAR ALUMNO ----------
@main_routes.route('/alumno/editar/<int:id>', methods=['GET', 'POST'])
def editar_alumno(id):
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    alumno = Alumno.query.get_or_404(id)

    if session.get('rango', 0) < 2:
        flash("No tenés permiso para editar alumnos", "warning")
        return redirect(url_for('main.alumnos'))

    if request.method == 'POST':
        grado_str = request.form.get('grado', '').strip()
        grado_num = int(grado_str[0]) if grado_str and grado_str[0].isdigit() else 0
        especialidad = request.form.get('especialidad') if grado_num >= 4 else None

        alumno.nombre = request.form.get('nombre', '').strip()
        alumno.apellido = request.form.get('apellido', '').strip()
        alumno.domicilio = request.form.get('domicilio', '').strip()
        alumno.email = request.form.get('email', '').strip()
        alumno.edad = int(request.form.get('edad', 0)) if request.form.get('edad') else None
        alumno.telefono = request.form.get('telefono', '').strip()
        alumno.grado = grado_str
        alumno.division = request.form.get('division', '').strip()
        alumno.especialidad = especialidad

        db.session.commit()
        flash("Alumno actualizado correctamente", "success")
        return redirect(url_for('main.alumnos'))

    return render_template('alumno_form.html', alumno=alumno)


# ---------- BORRAR ALUMNO ----------
@main_routes.route('/alumno/borrar/<int:id>', methods=['GET'])
def borrar_alumno(id):
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    if session.get('rango', 0) < 2:
        flash("No tenés permiso para borrar alumnos", "warning")
        return redirect(url_for('main.alumnos'))

    alumno = Alumno.query.get_or_404(id)
    db.session.delete(alumno)
    db.session.commit()
    flash("Alumno borrado correctamente", "success")
    return redirect(url_for('main.alumnos'))


# ---------- CONFIGURACIÓN ----------
@main_routes.route('/configuracion')
def configuracion():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    if session.get('rango', 0) >= 4:
        usuarios = Usuario.query.filter(Usuario.rango <= 5).all()
    else:
        usuarios = []

    return render_template('configuracion.html', usuarios=usuarios)


# ---------- NUEVO USUARIO ----------
@main_routes.route('/usuario/nuevo', methods=['GET', 'POST'])
def nuevo_usuario():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    if session.get('rango', 0) < 4:
        flash("No tenés permiso para crear usuarios", "warning")
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        apellido = request.form.get('apellido', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        try:
            rango = int(request.form.get('rango', 0))
        except ValueError:
            flash("Rango inválido", "danger")
            return redirect(request.url)

        if rango not in [1, 2, 3, 4, 5, 777]:
            flash("Rango inválido. Debe ser 1,2,3,4,5 o 777", "danger")
            return redirect(request.url)

        if not password:
            flash("Contraseña obligatoria", "danger")
            return redirect(request.url)

        if Usuario.query.filter_by(email=email).first():
            flash("Ya existe un usuario con ese email", "danger")
            return redirect(request.url)

        usuario = Usuario(nombre=nombre, apellido=apellido, email=email, rango=rango)
        usuario.set_password(password)
        db.session.add(usuario)
        db.session.commit()
        flash("Usuario creado correctamente", "success")
        return redirect(url_for('main.configuracion'))

    return render_template('usuario_form.html', usuario=None)


# ---------- EDITAR USUARIO ----------
@main_routes.route('/usuario/editar/<int:id>', methods=['GET', 'POST'])
def editar_usuario(id):
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    if session.get('rango', 0) < 4:
        flash("No tenés permiso para editar usuarios", "warning")
        return redirect(url_for('main.dashboard'))

    usuario = Usuario.query.get_or_404(id)

    if request.method == 'POST':
        usuario.nombre = request.form.get('nombre', '').strip()
        usuario.apellido = request.form.get('apellido', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        try:
            rango = int(request.form.get('rango', 0))
        except ValueError:
            flash("Rango inválido", "danger")
            return redirect(request.url)

        if rango not in [1, 2, 3, 4, 5, 777]:
            flash("Rango inválido. Debe ser 1,2,3,4,5 o 777", "danger")
            return redirect(request.url)

        if email != usuario.email and Usuario.query.filter_by(email=email).first():
            flash("Ya existe un usuario con ese email", "danger")
            return redirect(request.url)

        usuario.email = email
        usuario.rango = rango

        if password:
            usuario.set_password(password)

        db.session.commit()
        flash("Usuario actualizado correctamente", "success")
        return redirect(url_for('main.configuracion'))

    return render_template('usuario_form.html', usuario=usuario)


# ---------- BORRAR USUARIO ----------
@main_routes.route('/usuario/borrar/<int:id>', methods=['GET'])
def borrar_usuario(id):
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    if session.get('rango', 0) < 4:
        flash("No tenés permiso para borrar usuarios", "warning")
        return redirect(url_for('main.dashboard'))

    usuario = Usuario.query.get_or_404(id)
    db.session.delete(usuario)
    db.session.commit()
    flash("Usuario borrado correctamente", "success")
    return redirect(url_for('main.configuracion'))


# ---------- FEEDBACK ----------
@main_routes.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    if request.method == 'POST':
        flash('Gracias por tu mensaje — lo revisaremos pronto.', 'success')
        return redirect(url_for('main.dashboard'))

    return render_template('feedback.html')


# ---------- MENSAJES ----------
@main_routes.route('/mensajes')
def mensajes():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    return render_template('mensajes.html')


# ---------- IMPORTAR ALUMNOS ----------
@main_routes.route('/alumnos/importar', methods=['GET', 'POST'])
def importar_alumnos():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    if session.get('rango', 0) < 2:
        flash("No tenés permiso para importar alumnos", "warning")
        return redirect(url_for('main.alumnos'))

    if request.method == 'POST':
        if 'archivo' not in request.files:
            flash("No se seleccionó ningún archivo", "danger")
            return redirect(request.url)

        file = request.files['archivo']

        if file.filename == '':
            flash("No se seleccionó ningún archivo", "danger")
            return redirect(request.url)

        if file and allowed_file(file.filename):
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)

            try:
                if filename.endswith('.csv'):
                    df = pd.read_csv(filepath)
                else:
                    df = pd.read_excel(filepath)

                required_cols = ['nombre', 'apellido', 'email', 'edad', 'domicilio',
                                 'telefono', 'grado', 'division', 'especialidad']

                if not all(col in df.columns for col in required_cols):
                    flash(f"Columnas incorrectas. Debe contener: {', '.join(required_cols)}", "danger")
                    return redirect(request.url)

                for _, row in df.iterrows():
                    alumno = Alumno(
                        nombre=row['nombre'],
                        apellido=row['apellido'],
                        email=row['email'],
                        edad=int(row['edad']) if pd.notna(row['edad']) else None,
                        domicilio=row['domicilio'],
                        telefono=row['telefono'],
                        grado=row['grado'],
                        division=row['division'],
                        especialidad=row['especialidad'] if pd.notna(row['especialidad']) else None
                    )
                    db.session.add(alumno)

                db.session.commit()
                flash(f"{len(df)} alumnos importados correctamente", "success")

            except Exception as e:
                flash(f"Error al procesar el archivo: {e}", "danger")

            finally:
                os.remove(filepath)

            return redirect(url_for('main.alumnos'))

        else:
            flash("Formato no permitido. Use .xlsx o .csv", "danger")
            return redirect(request.url)

    return render_template('importar_alumnos.html')

# ---------- SOLICITUDES: reemplazadas ----------
@main_routes.route('/solicitud/nueva/<int:alumno_id>', methods=['GET','POST'])
def crear_solicitud(alumno_id):
	if 'user_id' not in session:
		return redirect(url_for('main.login'))

	# Solo profesores (rango == 1) pueden crear solicitudes
	if session.get('rango',0) != 1:
		flash("Solo profesores pueden enviar solicitudes sobre alumnos.", "warning")
		return redirect(url_for('main.alumnos'))

	alumno = Alumno.query.get_or_404(alumno_id)

	if request.method == 'POST':
		tipo = request.form.get('tipo')
		motivo = request.form.get('motivo','').strip()
		if tipo not in ('modificar','borrar'):
			flash("Tipo de solicitud inválido.", "danger")
			return redirect(request.url)
		if not motivo:
			flash("Debés indicar un motivo.", "danger")
			return redirect(request.url)

		# evitar duplicados: misma solicitud pendiente del mismo usuario sobre el mismo alumno y tipo
		existe = Solicitud.query.filter_by(
			usuario_id=session['user_id'],
			alumno_id=alumno_id,
			tipo=tipo,
			estado='pendiente'
		).first()
		if existe:
			flash("Ya existe una solicitud pendiente similar.", "info")
			return redirect(url_for('main.alumnos'))

		s = Solicitud(
			tipo=tipo,
			motivo=motivo,
			alumno_id=alumno_id,
			usuario_id=session['user_id'],
			creado_en=datetime.utcnow(),
			estado='pendiente'
		)
		db.session.add(s)
		db.session.commit()
		flash("Solicitud enviada correctamente.", "success")
		return redirect(url_for('main.alumnos'))

	return render_template('solicitud_crear.html', alumno=alumno)


@main_routes.route('/solicitudes')
def listar_solicitudes():
	if 'user_id' not in session:
		return redirect(url_for('main.login'))

	# Solo usuarios con rango >= 4 (secretaría, director) pueden ver solicitudes
	if session.get('rango', 0) < 3:
		flash("No tenés permiso para ver las solicitudes.", "warning")
		return redirect(url_for('main.dashboard'))

	solicitudes = Solicitud.query.order_by(Solicitud.creado_en.desc()).all()

	# convertir JSON a dict para mostrarlo
	for sol in solicitudes:
		if sol.datos_nuevos:
			sol.datos_nuevos_dict = json.loads(sol.datos_nuevos)
		else:
			sol.datos_nuevos_dict = {}

	return render_template('solicitudes.html', solicitudes=solicitudes)


@main_routes.route('/solicitud/aprobar/<int:sol_id>', methods=['POST'])
def aprobar_solicitud(sol_id):
	if 'user_id' not in session:
		flash("Tienes que iniciar sesión.", "danger")
		return redirect(url_for('main.login'))

	# Verificar permisos por rango (solo >= 4)
	if session.get('rango', 0) < 3:
		flash("No tenés permiso para aprobar solicitudes.", "danger")
		return redirect(url_for('main.listar_solicitudes'))

	solicitud = Solicitud.query.get_or_404(sol_id)
	alumno = Alumno.query.get_or_404(solicitud.alumno_id)

	# Aplicar cambios si hay datos nuevos
	if solicitud.datos_nuevos:
		nuevos = json.loads(solicitud.datos_nuevos)
		for campo, valor in nuevos.items():
			if valor not in (None, "", " "):
				setattr(alumno, campo, valor)

	solicitud.estado = "aprobada"
	solicitud.aprobador_id = session['user_id']
	db.session.commit()

	flash("Solicitud aprobada correctamente.", "success")
	return redirect(url_for('main.listar_solicitudes'))


@main_routes.route('/solicitud/rechazar/<int:sol_id>', methods=['POST'])
def rechazar_solicitud(sol_id):
	if 'user_id' not in session:
		flash("Tienes que iniciar sesión.", "danger")
		return redirect(url_for('main.login'))

	if session.get('rango', 0) < 3:
		flash("No tenés permiso para rechazar solicitudes.", "danger")
		return redirect(url_for('main.listar_solicitudes'))

	solicitud = Solicitud.query.get_or_404(sol_id)
	solicitud.estado = "rechazada"
	solicitud.aprobador_id = session['user_id']
	db.session.commit()

	flash("Solicitud rechazada.", "warning")
	return redirect(url_for('main.listar_solicitudes'))


@main_routes.route('/solicitar_edicion/<int:alumno_id>', methods=['GET', 'POST'])
def solicitar_edicion(alumno_id):
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    alumno = Alumno.query.get_or_404(alumno_id)

    # Solo profesores
    if session.get('rango', 0) != 1:
        flash("Solo profesores pueden solicitar ediciones.", "warning")
        return redirect(url_for('main.alumnos'))

    if request.method == 'POST':
        motivo = request.form.get('motivo', '').strip()

        if not motivo:
            flash("Debés indicar un motivo.", "danger")
            return redirect(request.url)

        # Datos nuevos
        nuevos_datos = {
            "nombre": request.form.get('nombre', '').strip(),
            "apellido": request.form.get('apellido', '').strip(),
            "domicilio": request.form.get('domicilio', '').strip(),
            "email": request.form.get('email', '').strip(),
            "edad": request.form.get('edad', '').strip(),
            "telefono": request.form.get('telefono', '').strip(),
            "grado": request.form.get('grado', '').strip(),
            "division": request.form.get('division', '').strip()
        }

        # Guardar solicitud correctamente
        solicitud = Solicitud(
            tipo="editar",
            motivo=motivo,
            estado="pendiente",
            alumno_id=alumno_id,
            usuario_id=session['user_id'],
            creado_en=datetime.utcnow(),
            datos_nuevos=json.dumps(nuevos_datos)  # <-- AQUÍ EL FIX
        )

        db.session.add(solicitud)
        db.session.commit()

        flash("Solicitud de edición enviada correctamente.", "success")
        return redirect(url_for('main.alumnos'))

    return render_template('solicitar_edicion.html', alumno=alumno)
