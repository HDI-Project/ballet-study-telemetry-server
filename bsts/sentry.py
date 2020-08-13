from os import getenv

import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration


def init_sentry():
    sentry_sdk.init(
        dsn=getenv('SENTRY_DSN'),
        environment=getenv('ENVIRONMENT'),
        integrations=[FlaskIntegration()]
    )
