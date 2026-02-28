from .extensions import db
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# --- 1. USUARIOS ---
class User(UserMixin, db.Model):
    __tablename__ = 'nsusers'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# --- 2. CLASE PADRE: DOCUMENTO ---
class Documento(db.Model):
    __tablename__ = 'nsdocumentos'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    discriminator = db.Column(db.String(20)) # 'presupuesto', 'albaran', 'factura'
    
    # Datos Comunes
    idempresa = db.Column(db.String(25), default='')
    numdocumento = db.Column(db.String(50))
    fechadocumento = db.Column(db.String(10))
    emisor = db.Column(db.String(255))
    cifemisor = db.Column(db.String(25))
    
    # Totales y Estado
    importebruto = db.Column(db.Numeric(10, 2), default=0.00)
    importeiva = db.Column(db.Numeric(10, 2), default=0.00)
    importeneto = db.Column(db.Numeric(10, 2), default=0.00)
    estado = db.Column(db.String(20), default='borrador')
    
    # Auditoría
    usuariocreacion = db.Column(db.String(25))
    auditcreacion = db.Column(db.DateTime, default=datetime.utcnow)

    # Relaciones (Líneas y Validaciones)
    lineas = db.relationship('DocumentoLinea', backref='cabecera', cascade="all, delete-orphan")
    validaciones = db.relationship('DocumentoValidacion', backref='cabecera', cascade="all, delete-orphan")

    __mapper_args__ = {
        'polymorphic_identity': 'documento',
        'polymorphic_on': discriminator
    }

    def validar_basico(self):
        """Validación de totales que aplica a todos"""
        errors = []
        # Sumamos las líneas usando los objetos de la BD
        suma_lineas = sum(float(l.preciototal) for l in self.lineas)
        if abs(suma_lineas - float(self.importebruto)) > 0.05:
            errors.append({
                "variable": "importebruto",
                "descripcion": f"Descuadre: La suma de líneas ({suma_lineas}) no coincide con el total ({self.importebruto}).",
                "error": 1
            })
        return errors

# --- 3. CLASES HIJAS ---
class Presupuesto(Documento):
    __tablename__ = 'nspresupuestos'
    id = db.Column(db.Integer, db.ForeignKey('nsdocumentos.id'), primary_key=True)
    fechavalidez = db.Column(db.String(10))
    __mapper_args__ = {'polymorphic_identity': 'presupuesto'}

    def validar_erp(self):
        """Lógica de validación para presupuestos"""
        res = self.validar_basico() # Empezamos con la básica
        # Aquí añadirías lógica específica contra el ERP
        if not self.cifemisor:
            res.append({"variable": "cifemisor", "descripcion": "Falta el CIF del emisor.", "error": 1})
        return res

class Albaran(Documento):
    __tablename__ = 'nsalbaranes'
    id = db.Column(db.Integer, db.ForeignKey('nsdocumentos.id'), primary_key=True)
    num_pedido_erp = db.Column(db.String(50))
    __mapper_args__ = {'polymorphic_identity': 'albaran'}

    def validar_erp(self):
        """Lógica de validación para albaranes"""
        res = self.validar_basico()
        if not self.num_pedido_erp:
            res.append({"variable": "num_pedido_erp", "descripcion": "El albarán no está vinculado a un pedido en el ERP.", "error": 1})
        return res

# --- 4. TABLA DE LÍNEAS (UNIFICADA) ---
class DocumentoLinea(db.Model):
    __tablename__ = 'nsdocumentos_lineas'
    id = db.Column(db.Integer, primary_key=True)
    documento_id = db.Column(db.Integer, db.ForeignKey('nsdocumentos.id'))
    numlinea = db.Column(db.Integer)
    referencia = db.Column(db.String(50))
    descripcion = db.Column(db.String(500))
    unidades = db.Column(db.Numeric(10, 2))
    preciounitario = db.Column(db.Numeric(12, 4))
    preciototal = db.Column(db.Numeric(10, 2))

# --- 5. TABLA DE VALIDACIONES (UNIFICADA) ---
class DocumentoValidacion(db.Model):
    __tablename__ = 'nsdocumentos_validaciones'
    id = db.Column(db.Integer, primary_key=True)
    documento_id = db.Column(db.Integer, db.ForeignKey('nsdocumentos.id'))
    numlinea = db.Column(db.Integer, default=0) # 0 para cabecera, >0 para líneas
    variable = db.Column(db.String(50))
    errordescripcion = db.Column(db.Text)
    error = db.Column(db.Integer, default=1) # 1: Error Crítico, 0: Aviso
    active = db.Column(db.Integer, default=1)