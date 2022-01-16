import pandas as pd
from googleapiclient.discovery import build
from google.oauth2 import service_account


def insert_values_in_gsheets(df,accBalance, spend ,delta_percentual, period_of_time):

    # Google Sheet Id das respostas ao formulário Ativação Bandeiras
    gsheet_id = '1pdHPpnOhA8_dvMKL9rbiUFYY5eo3urH8kKRSFSvyksg'
    SERVICE_ACCOUNT_FILE = r'credentials.json'
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    creds = None
    creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    
    service = build('sheets', 'v4', credentials=creds)

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

    # escrevendo saldo total na célula B3
    service.spreadsheets().values().update(
        spreadsheetId=gsheet_id,
        valueInputOption='RAW',
        range='main!C4',
        body= dict(
            majorDimension='ROWS',
            values=[[int(accBalance)]]
        )
    ).execute()

    # escrevendo gastos (R$)
    service.spreadsheets().values().update(
        spreadsheetId=gsheet_id,
        valueInputOption='RAW',
        range='main!C6',
        body= dict(
            majorDimension='ROWS',
            values=[[spend[0]],[spend[1]],[spend[2]]]
        )
    ).execute()

    # escrevendo aumento/decrescimento de gastos (%)
    service.spreadsheets().values().update(
        spreadsheetId=gsheet_id,
        valueInputOption='RAW',
        range='main!D6',
        body= dict(
            majorDimension='ROWS',
            values=[[delta_percentual[0]],[delta_percentual[1]],[delta_percentual[2]]]
        )
    ).execute()
    # escrevendo período de tempo abrangido
    service.spreadsheets().values().update(
        spreadsheetId=gsheet_id,
        valueInputOption='RAW',
        range='main!E6',
        body= dict(
            majorDimension='ROWS',
            values= [period_of_time[0],period_of_time[1],period_of_time[2]]
        )
    ).execute()