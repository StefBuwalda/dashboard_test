# import requests as r
from flask import jsonify, Flask
from poll_services import start_async_loop
from mem import services
import threading


# Flask app to serve status
app = Flask(__name__)


@app.route("/")
def status():
    return jsonify([s.to_dict() for s in services])


# Only run if directly running file
if __name__ == "__main__":

    t = threading.Thread(target=start_async_loop, daemon=True)
    t.start()

    # Run flask app
    app.run(debug=True, use_reloader=False)
