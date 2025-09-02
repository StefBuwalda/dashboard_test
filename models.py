from mem import db
from datetime import datetime, timezone


class log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dateCreated = db.Column(db.DateTime, nullable=False)

    def __init__(self):
        super().__init__()

        self.dateCreated = datetime.now(timezone.utc)
