from app import app
from flask_migrate import migrate

with app.app_context():
    migrate()
