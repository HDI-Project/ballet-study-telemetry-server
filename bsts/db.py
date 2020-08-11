from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Participant(db.Model):
    __tablename__ = 'participants'

    github_sha1 = db.Column(db.String(40), primary_key=True, nullable=False)
    optedin = db.Column(db.Boolean(), nullable=False)


class Event(db.Model):
    __tablename__ = 'events'

    id = db.Column(db.String(36), primary_key=True)
    host_sha1 = db.Column(db.String(40), nullable=False)
    github_sha1 = db.Column(db.String(40), nullable=True)
    name = db.Column(db.String(100), nullable=False)
    dt = db.Column(db.String(26), nullable=False)
    details = db.Column(db.Text(), nullable=True)
