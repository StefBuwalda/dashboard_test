from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, upgrade, stamp
from .flask_app import app
from pathlib import Path

__all__ = ["app"]

# Create db
db = SQLAlchemy(app=app)

# Set up migration
migration = Migrate(app=app, db=db)

# Init and upgrade
with app.app_context():
    # Check if DB file is missing
    if not (Path("./instance/app.db").is_file()):
        db.create_all()
        stamp()
    # Upgrade db if any new migrations exist
    upgrade()
