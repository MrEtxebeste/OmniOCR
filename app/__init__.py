import os
from flask import Flask
from .extensions import db, migrate

def create_app():
    app = Flask(__name__)
    
    # Configuración de MariaDB
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Inicializar extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    
    # IMPORTANTE: Importar los modelos aquí para que Flask-Migrate los vea
    from . import models 
    
    @app.route('/ping')
    def ping():
        return "¡Conexión establecida y modelos cargados!"
        
    return app