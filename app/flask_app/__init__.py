import threading
from flask import Flask

stop_event = threading.Event()

# Flask app to serve status
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"


def start_flask() -> None:
    try:
        # Run flask app
        from .routes import bp

        app.register_blueprint(bp)
        app.run(host="0.0.0.0", port=80, debug=True, use_reloader=False)
    except Exception as e:
        print("Worker thread exception:", e)
        stop_event.set()
