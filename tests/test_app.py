import datetime
import uuid

from bsts.db import Event
from bsts.util import sha1

API_PREFIX = '/api/v1'


def test_status(client):
    response = client.get('/status')
    assert response.status_code == 200
    assert b'OK' in response.data


def test_optedin(client):
    id = sha1('gh')
    response = client.get(API_PREFIX + f'/optedin?id={id}')
    assert response.status_code == 200
    assert 'unknown' in response.data.decode()


def test_events(client):
    data = [
        {
            'id': str(uuid.uuid4()),
            'host': sha1('host'),
            'gh': sha1('gh'),
            'name': 'binderlaunched',
            'dt': datetime.datetime.utcnow().isoformat(),
            'details': '',
        },
        {
            'id': str(uuid.uuid4()),
            'host': sha1('host'),
            'gh': sha1('gh'),
            'name': 'binderlaunched',
            'dt': datetime.datetime.utcnow().isoformat(),
            'details': '',
        }
    ]

    response = client.post(API_PREFIX + '/events', json=data)
    assert response.status_code == 200
    assert str(len(data)) in response.data.decode()

    events = Event.query.all()
    assert len(events) == len(data)
