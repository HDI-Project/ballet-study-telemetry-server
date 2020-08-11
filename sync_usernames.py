import base64
import json
import logging.config
import time
from os import getenv
from typing import Iterator, NoReturn, Tuple

import schedule
import funcy as fy
from google.oauth2 import service_account
from googleapiclient.discovery import Resource, build

from bsts import create_app
from bsts.db import db, Participant
from bsts.util import sha1

logging.config.fileConfig('logging.conf')
logger = logging.getLogger(__name__)


SCOPES = [
    'https://www.googleapis.com/auth/drive.readonly',
    'https://www.googleapis.com/auth/spreadsheets.readonly',
]
SPREADSHEET_RANGE = 'L:M'


@fy.decorator
def log_exceptions(call):
    try:
        return call()
    except Exception:  # pylint: disable=broad-except
        logger.exception(f'Exception in calling {call._func.__name__}')


def encode_service_account_info_file(path: str) -> str:
    # encode using json and b64 (to not worry about ctrl chars)
    # then dump to .env if you want
    with open(path, 'r') as f:
        info = json.load(f)
    return base64.b64encode(json.dumps(info).encode('utf-8'))


def load_service_account_info() -> str:
    return json.loads(base64.b64decode(getenv('GOOGLE_SERVICE_ACCOUNT')))


def create_service(kind: str, version: str) -> Resource:
    service_account_info = load_service_account_info()
    credentials = service_account.Credentials.from_service_account_info(
        service_account_info,
        scopes=SCOPES,
    )
    return build(kind, version, credentials=credentials, cache_discovery=False)


def create_drive_service() -> Resource:
    return create_service('drive', 'v3')


def create_sheets_service() -> Resource:
    return create_service('sheets', 'v4')


def get_survey_responses(sheets) -> dict:
    """Get optout survey responses (i.e. columns I and J)

    Returns:
        dict with keys range (str), majorDimension (str), and values
            List[List[str]]
    """
    spreadsheet_id = getenv('SPREADSHEET_ID')
    # sheet_id = '1063227223'  # does not appear to be needed

    range_ = SPREADSHEET_RANGE
    major_dimension = 'COLUMNS'

    request = (
        sheets
        .spreadsheets()
        .values()
        .get(spreadsheetId=spreadsheet_id,
             range=range_,
             majorDimension=major_dimension)
    )
    response = request.execute()
    return response


def get_username_optedin_pairs() -> Iterator[Tuple[str, str]]:
    sheets = create_sheets_service()
    survey_responses = get_survey_responses(sheets)
    usernames, optouts = survey_responses['values']

    # advance past header row!
    optouts, usernames = optouts[1:], usernames[1:]

    for i, username in enumerate(usernames):
        optedout = len(optouts) > i and optouts[i] == 'Opt out'
        optedin = not optedout
        github_sha1 = sha1(username)
        yield github_sha1, optedin


@log_exceptions
def sync_usernames() -> int:
    participants = []
    for github_sha1, optedin in get_username_optedin_pairs():
        if Participant.query.get(github_sha1) is None:
            participants.append(
                Participant(github_sha1=github_sha1, optedin=optedin))

    db.session.add_all(participants)
    db.session.commit()

    n = len(participants)
    logger.info(f'Synced {n} participants')
    return n


def main() -> NoReturn:
    app = create_app()
    with app.app_context():
        schedule.every(5).minutes.do(sync_usernames)
        schedule.run_all()
        while True:
            schedule.run_pending()
            time.sleep(1)


if __name__ == '__main__':
    main()
