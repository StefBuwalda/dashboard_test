from app import db


class logs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dateCreated = db.Column(db.DateTime, nullable=False)
