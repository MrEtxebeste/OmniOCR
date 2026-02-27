from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Instanciamos la base de datos y el motor de migraciones
db = SQLAlchemy()
migrate = Migrate()