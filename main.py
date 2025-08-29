# import requests as r
from flask import jsonify, Flask
from poll_services import update_services
from mem import services
import threading


# Flask app to serve status
app = Flask(__name__)


@app.route("/")
def status():
    return jsonify([s.to_dict() for s in services])


# Only run if directly running file
if __name__ == "__main__":
    threading.Thread(target=update_services, daemon=True).start()

    # Run flask app
    app.run(debug=True, use_reloader=False)
