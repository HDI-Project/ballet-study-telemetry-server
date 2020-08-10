import tempfile

import flask
import pytest
import werkzeug

from bsts import create_app
from bsts.conf import Config


@pytest.fixture
def app(monkeypatch) -> flask.Flask:
    db_fd, db_path = tempfile.mkstemp()
    monkeypatch.setattr(Config, 'SQLALCHEMY_DATABASE_URI', f'sqlite:///{db_path}')

    app = create_app(testing=True)
    app.config['TESTING'] = True
    with app.app_context():
        yield app


@pytest.fixture
def client(app: flask.Flask) -> werkzeug.test.Client:
    return app.test_client()
