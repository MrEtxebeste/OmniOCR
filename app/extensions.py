
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager # Añade esto

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager() # Añade esto
login_manager.login_view = 'auth.login' # Define a dónde redirigir si no está logueado