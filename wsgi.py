import logging.config
logging.config.fileConfig('logging.conf')

from bsts import create_app
app = create_app()
app.app_context().push()
