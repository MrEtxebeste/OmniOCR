import os
from flask import Flask
from .extensions import db, migrate

def create_app():
    app = Flask(__name__)
    
    # Leer la URL de MariaDB desde el archivo .env
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Inicializar extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    
    @app.route('/ping')
    def ping():
        return "¡OmniOCR está vivo y conectado a MariaDB!"
        
    return app