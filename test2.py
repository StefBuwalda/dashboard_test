# import requests as r
from flask import jsonify, Flask
from typing import Any, Optional


class service:
    url: str
    status: Optional[int]
    online: bool
    private: bool

    def __init__(self, url: str = "", private: bool = False):
        self.url = url
        self.private = private

        self.online = False
        self.status = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "url": self.url,
            "status": self.status,
            "private": self.private,
            "online": self.online,
        }

    def set_status(self, status: int):
        self.status = status


services: list[service] = [
    service("https://git.ihatemen.uk"),
    service("https://plex.ihatemen.uk"),
    service("https://truenas.local", True),
]

# Flask app to serve status
app = Flask(__name__)


@app.route("/")
def status():
    return jsonify([s.to_dict() for s in services])


# Only run if directly running file
if __name__ == "__main__":
    app.run(debug=True)
