from .extensions import db
from datetime import datetime
from flask_login import UserMixin # Añade esto
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash # Añade esto

class User(UserMixin, db.Model): # Añade UserMixin aquí
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    # Método para cifrar la contraseña al crear el usuario
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # Método para verificar la contraseña al hacer login
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Presupuesto(db.Model):
    __tablename__ = 'nspresupuestos'  # Nombre exacto de tu tabla en MariaDB

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    session = db.Column(db.String(25))
    idempresa = db.Column(db.String(25))
    tipodocumento = db.Column(db.String(25))
    numdocumento = db.Column(db.String(50))
    fechadocumento = db.Column(db.String(10))
    fechavalidez = db.Column(db.String(10))
    emisor = db.Column(db.String(255))
    naturaleza = db.Column(db.String(15), default='MAT')
    numpedidocliente = db.Column(db.String(50))
    numpedidoproveedor = db.Column(db.String(50))
    cifemisor = db.Column(db.String(25))
    estado = db.Column(db.Integer, default=10)
    codigoproveedorbc = db.Column(db.String(50))
    codigoproyectobc = db.Column(db.String(50))
    numalbaran = db.Column(db.String(50), nullable=True)
    importebruto = db.Column(db.Float(10, 2), default=0.00)
    importeiva = db.Column(db.Float(10, 2), default=0.00)
    importeneto = db.Column(db.Float(10, 2), default=0.00)
    porcentajeiva = db.Column(db.Float(10, 2), default=21.00)
    pdf = db.Column(db.LargeBinary, nullable=True) # Para el Longblob
    data = db.Column(db.Text) # El JSON completo de la IA
    hash = db.Column(db.String(32))
    tiempoproceso = db.Column(db.Integer)
    tokensentrada = db.Column(db.Integer)
    tokenssalida = db.Column(db.Integer)
    tokensinterno = db.Column(db.Integer)
    tokenstotal = db.Column(db.Integer)
    usuariocreacion = db.Column(db.String(25))
    auditcreacion = db.Column(db.String(19))
    usuariomodificacion = db.Column(db.String(25))
    auditmodificacion = db.Column(db.String(19))
    search = db.Column(db.Text)

# Añadir al final de app/models.py

class PresupuestoLinea(db.Model):
    __tablename__ = 'nspresupuestoslineas'

    # En SQLAlchemy necesitamos definir la clave primaria. 
    # Como 'ir' es el ID de la cabecera, usamos una clave compuesta (ir + numlinea)
    ir = db.Column(db.Integer, primary_key=True) 
    numlinea = db.Column(db.Integer, primary_key=True)
    
    idempresa = db.Column(db.String(25))
    tipodocumento = db.Column(db.String(25))
    numdocumento = db.Column(db.String(50))
    articulobc = db.Column(db.String(50))
    codigoproyectobc_line = db.Column(db.String(50), nullable=True)
    naturaleza = db.Column(db.String(10), nullable=True)
    referencia = db.Column(db.String(50))
    descripcion = db.Column(db.String(500))
    unidades = db.Column(db.Numeric(10, 2))
    preciounitario = db.Column(db.Numeric(12, 6))
    preciototal = db.Column(db.Numeric(10, 2))
    descuento = db.Column(db.Numeric(10, 2), default=0.00)
    procesado = db.Column(db.Boolean, default=False)
    
    usuariocreacion = db.Column(db.String(25))
    auditcreacion = db.Column(db.String(19))
    usuariomodificacion = db.Column(db.String(25))
    auditmodificacion = db.Column(db.String(19))
    search = db.Column(db.Text)

class PresupuestoValidacion(db.Model):
    __tablename__ = 'nspresupuestosvalidaciones'

    ir = db.Column(db.Integer, primary_key=True)
    numvalidacion = db.Column(db.Integer, primary_key=True)
    
    idempresa = db.Column(db.String(25))
    tipodocumento = db.Column(db.String(25))
    numdocumento = db.Column(db.String(50))
    numlinea = db.Column(db.Integer)
    variable = db.Column(db.String(50))
    errordescripcion = db.Column(db.Text)
    error = db.Column(db.Integer)
    active = db.Column(db.Integer, default=1)