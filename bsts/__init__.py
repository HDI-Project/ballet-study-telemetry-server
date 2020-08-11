from flask import Flask
from sqlalchemy.exc import OperationalError


def create_app(testing=False):
    app = Flask(__name__)
    app.config.from_object('bsts.conf.Config')

    if testing:
        app.config.from_object('bsts.conf.TestConfig')

    # create tables
    from bsts.db import db
    db.init_app(app)
    try:
        db.create_all(app=app)
        app.logger.info('db.create_all: created tables')
    except OperationalError:
        app.logger.info('db.create_all: did NOT create tables, they probably exist already')

    # add generic status page
    @app.route('/status')
    def status():
        return 'OK'

    # register API
    from bsts.api import api
    app.register_blueprint(api, url_prefix='/api/v1')

    app.logger.info(f'Logging from app {app.name}')

    return app
