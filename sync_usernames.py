import base64
import json
import logging.config
import time
from os import getenv

import schedule
from google.oauth2 import service_account
from googleapiclient.discovery import build

from bsts import create_app
from bsts.db import db, Participant
from bsts.util import sha1

logging.config.fileConfig('logging.conf')
logger = logging.getLogger(__name__)


SCOPES = [
    'https://www.googleapis.com/auth/drive.readonly',
    'https://www.googleapis.com/auth/spreadsheets.readonly',
]
SPREADSHEET_ID = '1ReiSCrUU1C4z5K0m1GzsuP_xKNT0Xv2Ck-iPsc8QW9A'
SPREADSHEET_RANGE = 'I:J'
TEST_SPREADSHEET_ID = '1D6xAA9rfng0CT_fGTVUQoSSEKwhEushtuv7dwXRM4ug'


def create_service(kind, version):
    service_account_info = json.loads(
        base64.b64decode(
            getenv('GOOGLE_SERVICE_ACCOUNT')))

    credentials = service_account.Credentials.from_service_account_info(
        service_account_info,
        scopes=SCOPES,
    )

    return build(kind, version, credentials=credentials, cache_discovery=False)


def create_drive_service():
    return create_service('drive', 'v3')


def create_sheets_service():
    return create_service('sheets', 'v4')


def get_survey_responses(sheets, testing=False):
    spreadsheet_id = SPREADSHEET_ID
    # sheet_id = '1063227223'  # does not appear to be needed

    if testing:
        spreadsheet_id = TEST_SPREADSHEET_ID

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


def sync_usernames():
    sheets = create_sheets_service()
    survey_responses = get_survey_responses(sheets)
    optouts, usernames = survey_responses['values']

    # advance past header row!
    optouts, usernames = optouts[1:], usernames[1:]

    participants = []
    for optout, username in zip(optouts, usernames):
        if optout == 'Opt out':
            status = 'no'
        elif optout is None or optout == '':
            status = 'yes'
        else:
            status = 'unknown'

        github_sha1 = sha1(username)

        if Participant.query.get(github_sha1) is None:
            participants.append(
                Participant(github_sha1=github_sha1, status=status))

    db.session.add_all(participants)
    db.session.commit()

    logger.info(f'Synced {len(participants)} participants')


def main():
    app = create_app()
    with app.app_context():
        schedule.every(5).minutes.do(sync_usernames)
        schedule.run_all()
        while True:
            schedule.run_pending()
            time.sleep(1)


if __name__ == '__main__':
    main()
