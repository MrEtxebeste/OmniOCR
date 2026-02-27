from .extensions import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doc_type = db.Column(db.String(20), nullable=False)  # factura, albaran, presupuesto
    filename = db.Column(db.String(255))
    supplier_name = db.Column(db.String(255))
    doc_date = db.Column(db.DateTime)
    total_base = db.Column(db.Float, default=0.0)
    total_tax = db.Column(db.Float, default=0.0)
    total_amount = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='pending') # pending, validated, synced
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relación con las líneas (1 documento -> N líneas)
    lines = db.relationship('DocumentLine', backref='document', lazy=True, cascade="all, delete-orphan")

class DocumentLine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('document.id'), nullable=False)
    description = db.Column(db.String(255))
    quantity = db.Column(db.Float, default=1.0)
    price_unit = db.Column(db.Float, default=0.0)
    tax_rate = db.Column(db.Float, default=21.0) # IVA por defecto
    total_line = db.Column(db.Float, default=0.0)