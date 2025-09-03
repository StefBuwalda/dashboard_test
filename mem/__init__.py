from typing import Any
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


class service:
    id: int
    url: str
    online: bool
    public: bool
    ping_type: int

    def __init__(
        self,
        id: int,
        url: str = "",
        label: str = "",
        public: bool = True,
        ping_type: int = 0,
    ):
        self.id = id
        self.url = url
        self.public = public
        self.label = label
        self.ping_type = ping_type

    def to_dict(self) -> dict[str, Any]:
        return {
            "url": self.url,
            "public": self.public,
            "label": self.label,
            "id": self.id,
            "ping_type": self.ping_type,
        }


services: list[service] = [
    service(0, "https://git.ihatemen.uk/", "Gitea"),
    service(1, "https://plex.ihatemen.uk/", "Plex"),
    service(2, "https://truenas.local/", "TrueNAS", False),
    service(3, "https://cloud.ihatemen.uk/", "NextCloud"),
    service(4, "https://request.ihatemen.uk/", "Overseerr"),
    service(5, "https://id.ihatemen.uk/", "PocketID"),
    service(6, "https://tautulli.local/", "Tautulli", False),
    service(
        7, "https://transmission.local/", "Transmission", False, ping_type=1
    ),
    service(8, "https://vault.ihatemen.uk/", "Vault Warden"),
    service(9, "https://nginx.local/", "Nginx (NPM)", False),
    service(10, "https://app.ihatemen.uk/", "Kcal Counter"),
    service(
        id=11, url="https://unifi.local/", label="Unifi Server", public=False
    ),
]

# Flask app to serve status
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"

db = SQLAlchemy(app=app)
migration = Migrate(app=app, db=db)
