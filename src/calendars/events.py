import datetime
import pickle
import os
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pandas as pd


class Events:

    @staticmethod
    def get_credentials(creds):
        SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('calendars/token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        return creds

    def get_next_events(self, nevents):
        """Access String Lab Google Calendar and views the next nevents events"""

        with open('calendars/token.pickle', 'rb') as f:
            credentials = pickle.load(f)

        credentials = self.get_credentials(credentials)
        service = build('calendar', 'v3', credentials=credentials)

        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        print(f'Getting the upcoming {nevents} events')
        events_result = service.events().list(calendarId='primary', timeMin=now,
                                              maxResults=nevents, singleEvents=True,
                                              orderBy='startTime').execute()

        return events_result

    @staticmethod
    def process_times(df):

        df['start'] = df['start'].apply(lambda x: x['dateTime'])
        df['end'] = df['end'].apply(lambda x: x['dateTime'])

        start_date = pd.to_datetime(df['start']).dt.date
        start_time = pd.to_datetime(df['start']).dt.time
        end_time = pd.to_datetime(df['end']).dt.time

        start_date = start_date.apply(lambda x: f'{str(x.day).zfill(2)}/{str(x.month).zfill(2)}')
        start_time = start_time.apply(lambda x: f'{str(x.hour).zfill(2)}:{str(x.minute).zfill(2)}')
        end_time = end_time.apply(lambda x: f'{str(x.hour).zfill(2)}:{str(x.minute).zfill(2)}')

        return start_date, start_time, end_time

    def next_3_events_information(self):

        events_result = self.get_next_events(3)

        if events_result['items']:

            events_data = pd.DataFrame(events_result['items'])

            events_data['start_date'], events_data['start'], events_data['end'] = self.process_times(events_data)

            info = events_data[['summary', 'start_date', 'start', 'end']].values

            return info

        return [['Não há eventos futuros.']]



