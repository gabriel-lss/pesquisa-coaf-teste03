from flask import Flask, render_template, request, redirect, url_for
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

app = Flask(__name__)

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '12VVy7-psknnAeQN48_wOruas-BFzpNW_7H9sYFQJf3A'
SAMPLE_RANGE_NAME = '202307_PEP!A2:I10'


def get_google_sheets_data(search_term):
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                    range=SAMPLE_RANGE_NAME).execute()
        values = result.get('values', [])

        if not values:
            return []

        data = []
        for row in values:
            # Check if the search term is in any cell of the row
            if any(search_term.lower() in cell.lower() for cell in row):
                data.append(row)

        return data

    except HttpError as err:
        print(err)
        return []


@app.route('/', methods=['GET', 'POST'])
def index():
    search_results = []
    if request.method == 'POST':
        search_term = request.form['search']
        search_results = get_google_sheets_data(search_term)
    return render_template('index.html', search_results=search_results)


if __name__ == '__main__':
    app.run(debug=True)
