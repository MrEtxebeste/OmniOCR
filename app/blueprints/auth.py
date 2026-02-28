from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_user, logout_user, login_required
import os
from werkzeug.utils import secure_filename
from ..models import *

from flask import request, flash, redirect, url_for, render_template, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from datetime import datetime

# Importamos las herramientas de IA y Base de Datos
from app.services.ai_provider.factory import AIFactory
from ..extensions import db

auth_bp = Blueprint('auth', __name__)

# Añade esto al final de app/blueprints/auth.py

@auth_bp.route('/documents/<type>')
@login_required
def list_documents(type):
    valid_types = ['factura', 'albaran', 'presupuesto']
    
    if type not in valid_types:
        flash("Tipo de documento no válido")
        return redirect(url_for('auth.dashboard'))
    
    docs = []
    
    # Por ahora solo leemos de la base de datos si es presupuesto
    # (Ya que es la tabla 'nspresupuestos' que hemos mapeado)
    if type == 'presupuesto':
        docs = Presupuesto.query.order_by(Presupuesto.auditcreacion.desc()).all()
    else:
        # Mensaje temporal hasta que mapeemos nsfacturas y nsalbaranes
        flash(f"La tabla para {type} aún no está conectada a Flask.")
    
    title = type.capitalize() + "s"
    
    return render_template('documents_list.html', documents=docs, title=title, doc_type=type)

# En app/blueprints/auth.py
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('auth.dashboard'))
        
        # Si falla:
        flash('Usuario o contraseña incorrectos')
        return redirect(url_for('auth.login')) # <--- REDIRIJE AQUÍ en vez de render_template
    
    return render_template('auth/login.html')



@auth_bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if request.method == 'POST':
        # 1. Verificar si el usuario ha enviado un archivo
        if 'file' not in request.files:
            flash('No se seleccionó ningún archivo')
            return redirect(request.url)
        
        file = request.files['file']
        doc_type = request.form.get('doc_type', 'presupuesto')

        if file.filename == '':
            flash('Nombre de archivo no válido')
            return redirect(request.url)

        if file:
            try:
                # 2. Guardar el archivo físicamente en la carpeta uploads
                filename = secure_filename(file.filename)
                upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
                file.save(upload_path)
                
                # 3. LLAMADA A LA IA (La magia del OCR)
                provider = AIFactory.get_provider()
                res = provider.extract_data(upload_path, doc_type)
                
                # 4. GUARDAR EN MARIADB (Cabecera y Líneas)
                if doc_type == 'presupuesto':
                    # Generar un número de documento si la IA no lo encuentra
                    num_doc_extraido = res.get('numdocumento')
                    if not num_doc_extraido or num_doc_extraido == 'null':
                        num_doc_extraido = f"PR-{datetime.now().strftime('%Y%m%d%H%M%S')}"

                    # -- A. CREAR CABECERA --
                    nuevo_presu = Presupuesto(
                        session = "SESION_WEB",       # Valor genérico para cumplir tu estructura
                        idempresa = "EMP001",         # Valor genérico para cumplir tu estructura
                        tipodocumento = "PRESUPUESTO",
                        numdocumento = num_doc_extraido,
                        fechadocumento = res.get('fechadocumento', datetime.now().strftime('%d/%m/%Y')),
                        emisor = res.get('emisor', 'Desconocido'),
                        cifemisor = res.get('cifemisor', ''),
                        importebruto = float(res.get('importebruto', 0.0)),
                        importeiva = float(res.get('importeiva', 0.0)),
                        importeneto = float(res.get('importeneto', 0.0)),
                        porcentajeiva = float(res.get('porcentajeiva', 21.0)),
                        data = str(res), # Guardamos el JSON completo por si acaso
                        usuariocreacion = current_user.username,
                        auditcreacion = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    )
                    db.session.add(nuevo_presu)
                    db.session.flush() # Envía los datos a MariaDB sin cerrar la transacción para verificar errores
                    
                    # -- B. CREAR LÍNEAS --
                    for i, linea in enumerate(res.get('lines', []), start=1):
                        nueva_linea = PresupuestoLinea(
                            idempresa = "EMP001",
                            tipodocumento = "PRESUPUESTO",
                            numdocumento = nuevo_presu.numdocumento, # Unimos la línea con la cabecera
                            numlinea = i,
                            descripcion = linea.get('descripcion', 'Sin descripción'),
                            unidades = float(linea.get('cantidad', 1.0)),
                            preciounitario = float(linea.get('precio_unidad', 0.0)),
                            preciototal = float(linea.get('total', 0.0)),
                            usuariocreacion = current_user.username,
                            auditcreacion = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        )
                        db.session.add(nueva_linea)

                    # -- C. CONFIRMAR TODO --
                    db.session.commit()
                    flash(f'¡Éxito! Presupuesto {nuevo_presu.numdocumento} procesado y guardado con sus líneas.')
                
                else:
                    flash(f'Archivo subido, pero la BD para el tipo {doc_type} aún no está configurada.')

            except Exception as e:
                # Si algo falla (la IA se cuelga, falla la base de datos, etc.) deshacemos todo
                db.session.rollback()
                flash(f'Ocurrió un error al procesar el documento: {str(e)}')

            return redirect(url_for('auth.dashboard'))

    return render_template('dashboard.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))