import pandas as pd
from googleapiclient.discovery import build
from google.oauth2 import service_account


def insert_values_in_gsheets(df,accBalance, spend ,delta_percentual, period_of_time,current_datetime):

    # Google Sheet Id das respostas ao formulário Ativação Bandeiras
    gsheet_id = '1pdHPpnOhA8_dvMKL9rbiUFYY5eo3urH8kKRSFSvyksg'
    SERVICE_ACCOUNT_FILE = r'creds/credentials.json'
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    creds = None
    creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    
    service = build('sheets', 'v4', credentials=creds)
    # updates data transactions_df in data_source sheet
    service.spreadsheets().values().update(
        spreadsheetId=gsheet_id,
        valueInputOption='RAW',
        range='data_source!A2',
        body= dict(
            majorDimension='ROWS',
            values=df.values.tolist()
        )
    ).execute()
    
    print("Current Savings:",accBalance)

    # writes date and current savings value
    service.spreadsheets().values().append(
        spreadsheetId=gsheet_id,
        valueInputOption='RAW',
        range='daily_savings!A:B',
        body= dict(
            majorDimension='ROWS',
            values=[[str(current_datetime),int(accBalance)]]
        )
    ).execute()