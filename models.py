from mem import db
from datetime import datetime, timezone
from validators import url as is_url
from typing import Any, Optional


class log(db.Model):
    id: int = db.Column(db.Integer, primary_key=True)  # TODO: Switch to UUID
    dateCreated: datetime = db.Column(db.DateTime, nullable=False, index=True)
    service_id: int = db.Column(
        db.Integer,
        db.ForeignKey("service.id"),
        nullable=False,
    )
    ping: Optional[int] = db.Column(db.Integer, nullable=True)

    def __init__(self, service_id: int, ping: Optional[int]):
        super().__init__()
        self.service_id = service_id
        self.ping = ping

        self.dateCreated = datetime.now(timezone.utc)


class service(db.Model):
    id: int = db.Column(db.Integer, primary_key=True)  # TODO: Switch to UUID
    url: str = db.Column(db.String, nullable=False)
    label: str = db.Column(db.String(15), nullable=False)
    public_access: bool = db.Column(db.Boolean, nullable=False)
    ping_method: int = db.Column(db.Integer, nullable=False)

    logs = db.relationship("log")

    def __init__(
        self, url: str, label: str, public_access: bool, ping_method: int
    ):
        if not is_url(url):
            raise Exception("URL IS NOT A VALID URL")
        if len(label) > 15:
            raise Exception("LABEL EXCEEDS MAXIMUM LENGTH (15)")
        super().__init__()
        self.url = url
        self.label = label
        self.public_access = public_access
        self.ping_method = ping_method

    def to_dict(self) -> dict[str, Any]:
        return {
            "url": self.url,
            "public_access": self.public_access,
            "label": self.label,
            "id": self.id,
            "ping_method": self.ping_method,
        }
