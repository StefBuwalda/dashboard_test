# import requests as r
from flask import jsonify, Flask, render_template, send_file
from poll_services import start_async_loop
from mem import services
import threading
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, init, upgrade
from pathlib import Path

# Flask app to serve status
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"

db = SQLAlchemy(app=app)
migration = Migrate(app=app, db=db)

# Init and upgrade
with app.app_context():
    # Check if DB file or migrations folder is missing
    if not (
        Path("./instance/app.db").is_file() and Path("./migrations").is_dir()
    ):
        init()
    # Upgrade db if any new migrations exist
    upgrade()


class logs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dateCreated = db.Column(db.DateTime, nullable=False)


@app.route("/")
def homepage():
    return render_template("home.html", services=services)


@app.route("/api/status")
def status():
    return jsonify([s.to_dict() for s in services])


@app.route("/favicon.svg")
def favicon():
    return send_file("/static/favicon.svg")


# Only run if directly running file
if __name__ == "__main__":

    t = threading.Thread(target=start_async_loop, daemon=True)
    t.start()

    # Run flask app
    app.run(host="0.0.0.0", port=80, debug=True, use_reloader=False)
