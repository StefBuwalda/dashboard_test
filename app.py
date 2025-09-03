# import requests as r
from flask import jsonify, render_template, send_file
from poll_services import start_async_loop
from mem import services, app, db
import threading
from flask_migrate import upgrade, stamp
from pathlib import Path
from models import service


# Init and upgrade
with app.app_context():
    # Check if DB file is missing
    if not (Path("./instance/app.db").is_file()):
        with app.app_context():
            db.create_all()
        stamp()
    # Upgrade db if any new migrations exist
    upgrade()

with app.app_context():
    if not db.session.query(service).first():
        for s in services:
            db.session.add(
                service(
                    url=s.url,
                    label=s.label,
                    public_access=s.public,
                    ping_method=s.ping_type,
                )
            )
        db.session.commit()


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
