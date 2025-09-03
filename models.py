from mem import db
from datetime import datetime, timezone


class log(db.Model):
    id: int = db.Column(db.Integer, primary_key=True)
    dateCreated: datetime = db.Column(db.DateTime, nullable=False)

    def __init__(self):
        super().__init__()

        self.dateCreated = datetime.now(timezone.utc)


class service(db.Model):
    id: int = db.Column(db.Integer, primary_key=True)  # TODO: Switch to UUID
    url: str = db.Column(db.String, nullable=False)
    label: str = db.Column(db.String(15), nullable=False)
    public_access: bool = db.Column(db.Boolean, nullable=False)
    ping_method: int = db.Column(db.Integer, nullable=False)

    def __init__(self):
        super().__init__()
