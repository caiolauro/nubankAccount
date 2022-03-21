import pandas as pd
from googleapiclient.discovery import build
from google.oauth2 import service_account


class SpreadSheet:
    
    id = '1pdHPpnOhA8_dvMKL9rbiUFYY5eo3urH8kKRSFSvyksg'
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    SERVICE_ACCOUNT_FILE = r'creds/credentials.json'
    

    @staticmethod
    def insert_values(df,accBalance, spend ,delta_percentual, period_of_time,current_datetime):
            
        creds = None
        creds = service_account.Credentials.from_service_account_file(
                SpreadSheet.SERVICE_ACCOUNT_FILE, scopes=SpreadSheet.SCOPES)
        
        service = build('sheets', 'v4', credentials=creds)
        
        # updates data transactions_df in transactions_record sheet
        service.spreadsheets().values().update(
            spreadsheetId=SpreadSheet.id,
            valueInputOption='RAW',
            range='transactions_record!A2',
            body= dict(
                majorDimension='ROWS',
                values=df.values.tolist()
            )
        ).execute()
        
        print("Current Savings:",accBalance)

        # writes date and current savings value on daily_savings
        service.spreadsheets().values().append(
            spreadsheetId=SpreadSheet.id,
            valueInputOption='RAW',
            range='daily_savings!A:B',
            body= dict(
                majorDimension='ROWS',
                values=[[str(current_datetime),int(accBalance)]]
            )
        ).execute()
        