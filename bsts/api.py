from flask import Blueprint, request
from bsts.db import db, Participant, Event

api = Blueprint('main', __name__)


@api.route('/optedin', methods=['GET'])
def optedin():
    github_sha1 = request.args['id']
    participant = (
        db.session
        .query(Participant)
        .get(github_sha1)
    )
    return participant.status if participant is not None else 'unknown'


@api.route('/events', methods=['POST'])
def events():
    body = request.get_json(force=True)
    events = []
    for element in body:
        events.append(Event(
            id=element['id'],
            host_sha1=element['host'],
            github_sha1=element['gh'],
            name=element['name'],
            dt=element['dt'],
            details=element['details'],
        ))
    db.session.add_all(events)
    db.session.commit()
    return str(len(events))
