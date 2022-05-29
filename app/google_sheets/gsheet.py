import pandas as pd
from googleapiclient.discovery import build
from google.oauth2 import service_account
import logging
logging.basicConfig(level=logging.DEBUG, filename='/mnt/c/users/caio.lauro/Documents/personal_projects/NuBankAPI/logs/api_call_log.log', format='%(asctime)s:%(levelname)s:%(message)s')

# variables
GSHEET_TRANSACTIONS_TAB = 'transactions_record!A2'
GSHEET_DAILY_SAVINGS_TAB = 'daily_savings!A:B'

class GSheet:
    
    id = '1pdHPpnOhA8_dvMKL9rbiUFYY5eo3urH8kKRSFSvyksg'
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    SERVICE_ACCOUNT_FILE = r'/mnt/c/users/caio.lauro/Documents/personal_projects/NuBankAPI/creds/credentials.json'
    

    def insert_values(self, df,accBalance,current_datetime):
            
        creds = None
        creds = service_account.Credentials.from_service_account_file(
                self.SERVICE_ACCOUNT_FILE, scopes=self.SCOPES)
        
        service = build('sheets', 'v4', credentials=creds)
        
        # updates data transactions_df in transactions_record sheet
        try:
            service.spreadsheets().values().update(
                spreadsheetId=self.id,
                valueInputOption='RAW',
                range=GSHEET_TRANSACTIONS_TAB,
                body= dict(
                    majorDimension='ROWS',
                    values=df.values.tolist()
                )
            ).execute()
        except Exception as e:
            logging.error(f"Error while updating {GSHEET_TRANSACTIONS_TAB}: {e}")
            #print(f"Error while updating {GSHEET_TRANSACTIONS_TAB}: {e}")
        
        print("Current Savings:",accBalance)

        # writes date and current savings value on daily_savings
        try:
            service.spreadsheets().values().append(
                spreadsheetId=self.id,
                valueInputOption='RAW',
                range=GSHEET_DAILY_SAVINGS_TAB,
                body= dict(
                    majorDimension='ROWS',
                    values=[[str(current_datetime),int(accBalance)]]
                )
            ).execute()
        except Exception as e:
            logging.error(f"Error while appending {GSHEET_DAILY_SAVINGS_TAB}: {e}")
            #print(f"Error while appending {GSHEET_DAILY_SAVINGS_TAB}: {e}")
        