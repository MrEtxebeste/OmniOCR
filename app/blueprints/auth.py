import os
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename

# Importamos nuestros modelos, base de datos y fábrica de IA
from ..models import User, Presupuesto, PresupuestoLinea, PresupuestoValidacion
from ..extensions import db
from app.services.ai_provider.factory import AIFactory

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('auth.dashboard'))
        
        flash('Usuario o contraseña incorrectos')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

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
                # 2. Guardar el archivo físicamente
                filename = secure_filename(file.filename)
                upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
                file.save(upload_path)
                
                # 3. LLAMADA A LA IA (Usando Pydantic por debajo)
                provider = AIFactory.get_provider()
                res = provider.extract_data(upload_path, doc_type)
                
                # Desempaquetamos los datos validados
                datos_cabecera = res['data']
                
                # 4. GUARDAR EN MARIADB
                if doc_type == 'presupuesto':
                    num_doc = datos_cabecera.get('numdocumento')
                    if not num_doc: # Si la IA no encontró número, generamos uno temporal
                        num_doc = f"PR-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                    
                    # -- A. CREAR CABECERA --
                    nuevo_presu = Presupuesto(
                        session="SESION_WEB",
                        idempresa=datos_cabecera.get('idempresa', 'EMP001'),
                        tipodocumento="PRESUPUESTO",
                        numdocumento=num_doc,
                        fechadocumento=datos_cabecera.get('fechadocumento'),
                        emisor=datos_cabecera.get('emisor'),
                        cifemisor=datos_cabecera.get('cifemisor'),
                        importebruto=datos_cabecera.get('importebruto', 0.0),
                        importeiva=datos_cabecera.get('importeiva', 0.0),
                        importeneto=datos_cabecera.get('importeneto', 0.0),
                        porcentajeiva=datos_cabecera.get('porcentajeiva', 0.0),
                        data=str(res),
                        usuariocreacion=current_user.username,
                        auditcreacion=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    )
                    db.session.add(nuevo_presu)
                    db.session.flush() # Genera el ID ('ir')
                    
                    header_id = nuevo_presu.id 

                    # -- B. CREAR LÍNEAS --
                    for linea in datos_cabecera.get('lines', []):
                        nueva_linea = PresupuestoLinea(
                            ir=header_id,
                            idempresa=nuevo_presu.idempresa,
                            tipodocumento="PRESUPUESTO",
                            numdocumento=nuevo_presu.numdocumento,
                            numlinea=linea.get('numlinea'),
                            articulobc=linea.get('articulobc'),
                            referencia=linea.get('referencia'),
                            descripcion=linea.get('descripcion'),
                            unidades=linea.get('unidades', 0.0),
                            preciounitario=linea.get('preciounitario', 0.0),
                            preciototal=linea.get('preciototal', 0.0),
                            descuento=linea.get('descuento', 0.0),
                            naturaleza=linea.get('naturaleza'),
                            usuariocreacion=current_user.username,
                            auditcreacion=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        )
                        db.session.add(nueva_linea)
                        
                    # -- C. CREAR VALIDACIONES --
                    for val in res.get('validaciones', []):
                        nueva_validacion = PresupuestoValidacion(
                            ir=header_id,
                            numvalidacion=val.get('numvalidacion'),
                            idempresa=nuevo_presu.idempresa,
                            tipodocumento="PRESUPUESTO",
                            numdocumento=nuevo_presu.numdocumento,
                            numlinea=val.get('numlinea', 0),
                            variable=val.get('variable'),
                            errordescripcion=val.get('errordescripcion'),
                            error=val.get('error', 0),
                            active=1
                        )
                        db.session.add(nueva_validacion)

                    # -- D. CONFIRMAR TODO JUNTO (Transacción Atómica) --
                    db.session.commit()
                    flash(f'¡Éxito! Presupuesto {nuevo_presu.numdocumento} guardado con sus líneas y validaciones.')
                
                else:
                    flash(f'Archivo subido, pero la BD para el tipo {doc_type} aún no está configurada.')

            except Exception as e:
                db.session.rollback()
                flash(f'Ocurrió un error al procesar el documento: {str(e)}')

            return redirect(url_for('auth.dashboard'))

    return render_template('dashboard.html')

@auth_bp.route('/documents/<type>')
@login_required
def list_documents(type):
    valid_types = ['factura', 'albaran', 'presupuesto']
    
    if type not in valid_types:
        flash("Tipo de documento no válido")
        return redirect(url_for('auth.dashboard'))
    
    docs = []
    
    if type == 'presupuesto':
        docs = Presupuesto.query.order_by(Presupuesto.auditcreacion.desc()).all()
    else:
        flash(f"La tabla para {type} aún no está conectada a Flask.")
    
    title = type.capitalize() + "s"
    return render_template('documents_list.html', documents=docs, title=title, doc_type=type)

# Añadir al final de app/blueprints/auth.py

@auth_bp.route('/document/<type>/<int:doc_id>',methods=['GET'])
@login_required
def view_document(type, doc_id):
    if type == 'presupuesto':
        # Buscamos la cabecera por su ID
        document = Presupuesto.query.get_or_404(doc_id)
        # Buscamos todas las líneas que tengan el 'ir' igual al ID de la cabecera
        lines = PresupuestoLinea.query.filter_by(ir=doc_id).order_by(PresupuestoLinea.numlinea).all()
        validaciones = PresupuestoValidacion.query.filter_by(ir=doc_id).all()
    else:
        flash(f"La vista detalle para {type} aún no está conectada.")
        return redirect(url_for('auth.list_documents', type=type))

    return render_template('document_detail.html', document=document, lines=lines, validaciones=validaciones, doc_type=type)