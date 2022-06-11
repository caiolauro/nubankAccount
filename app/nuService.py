from pynubank import Nubank
import logging
import json
import pandas as pd
import re
from datetime import datetime
from google_sheets.gsheet import GSheet
import os

logging.basicConfig(level=logging.DEBUG, filename='/mnt/c/users/caio.lauro/Documents/personal_projects/NuBankAPI/logs/api_call_log.log', format='%(asctime)s:%(levelname)s:%(message)s')

class nuService:

    nu:Nubank = None
    gsheet:GSheet = None
    currentDatetime = None
    freshToken:str = None
    creditCardTransactions:pd.DataFrame = None
    debitTransactions:pd.DataFrame = None
    fullTransactionsHistory:pd.DataFrame = None
    ITAU:float = 2600
    NU_INVEST:float = 600
    SELIC2022:float = 7201.38
    currentSavings:str = None
    
    @classmethod
    def inititalize(cls):
        cls.gsheet = GSheet()
        cls.currentDatetime = datetime.now().strftime('%Y-%m-%d')
        cls.nu = Nubank()
        cls.get_fresh_token()
        
    @classmethod
    def get_fresh_token(cls):
        cls.freshToken = cls.nu.authenticate_with_cert(os.getenv("NU_USER_LOGIN"), os.getenv("NU_PASSWORD"), r"/mnt/c/users/caio.lauro/Documents/personal_projects/NuBankAPI/creds/cert.p12")
        with open(r"/mnt/c/users/caio.lauro/Documents/personal_projects/NuBankAPI/creds/fresh_token", 'w') as token_file:
            token_file.write(cls.freshToken)

    @classmethod
    def get_credit_card_spend(cls):
        credit_transactions = cls.nu.get_card_statements() # Extrai compras feitas no cartão de crédito no formato JSON
        df = pd.json_normalize(credit_transactions)
        # Transformações no DataFrame
            # Selecionando Colunas
        credit_df = df[['description', 'category', 'amount', 'time', 'title','details.subcategory']]
            # Remove Caracteres da Couluna de 'Time'
        credit_df['time'] = credit_df['time'].apply(lambda x: x.replace("Z","").replace("T"," "))
            # Gerando colunas para diferentes granularidades de data a partir credit_df['time'].apply(lambda date: str(datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        credit_df.loc[:,'amount'] = credit_df['amount'] / 100
        credit_df.loc[:,'hour'] = credit_df['time'].apply(lambda date: str(datetime.strptime(date, '%Y-%m-%d %H:%M:%S').hour))
        credit_df.loc[:,'day'] = credit_df['time'].apply(lambda date: str(datetime.strptime(date, '%Y-%m-%d %H:%M:%S').day))
        credit_df.loc[:,'month'] = credit_df['time'].apply(lambda date: str(datetime.strptime(date, '%Y-%m-%d %H:%M:%S').month))
        credit_df.loc[:,'year'] = credit_df['time'].apply(lambda date: str(datetime.strptime(date, '%Y-%m-%d %H:%M:%S').year))
        cls.creditCardTransactions = credit_df

    @classmethod
    def get_debit_account_spend(cls):
        # Extraindo transações Nuconta
        account_statements = cls.nu.get_account_statements()
        # Criando dataframe 
        nuconta_df = pd.DataFrame(account_statements).fillna("NULL")

        # Criando coluna diferenciando o que é Entrada e Saída
        nuconta_df.loc[:,'is_income'] = nuconta_df['title'].apply(lambda x: True if x.lower().__contains__("recebid") or  x.lower().__contains__("devolvid") else False)
        # Remove 99pay
        nuconta_df_2 = nuconta_df.where(nuconta_df['detail'].str.contains("Adyen") == False).dropna()
        # remove pagamentos de fatura
        nuconta_df_2 = nuconta_df_2.where(nuconta_df['__typename']!='BillPaymentEvent').dropna()
        # tratamento da coluna details
        nuconta_df_2['detail'] = nuconta_df_2['detail'].apply(lambda x: ''.join(re.findall('\D',x)).replace('R$','').replace('\n','').replace(',','').replace('.',''))
        # seleciona colunas desejadas nuconta_df
        nuconta_df_2 = nuconta_df_2[['postDate', 'amount', 'is_income','detail']]
        new_columns = ['time','amount','is_income','detail']
        nuconta_df_2.columns = new_columns
        # Transformando valores das transações em tipo de dados Float
        nuconta_df_2.loc[:,'amount']  = nuconta_df_2['amount'].apply(lambda x: float(x))
        # Geração de Colunas de Data para nuconta_df_2
        nuconta_df_2.loc[:,'day'] = nuconta_df_2['time'].apply(lambda date: str(datetime.strptime(date, "%Y-%m-%d").day))
        nuconta_df_2.loc[:,'month'] = nuconta_df_2['time'].apply(lambda date: str(datetime.strptime(date, "%Y-%m-%d").month))
        nuconta_df_2.loc[:,'year'] = nuconta_df_2['time'].apply(lambda date: str(datetime.strptime(date, "%Y-%m-%d").year))
        nuconta_df_2.loc[:,'time'] = nuconta_df_2['time'] + ' 12:00:00'
        # Label para Nuconta
        nuconta_df_2.loc[:,'description'] = 'NULL'
        nuconta_df_2.loc[:,'category'] = 'Nuconta'
        cls.debitTransactions = nuconta_df_2
    @classmethod
    def merge_credit_and_debit_histories(cls):
        # Merge do Dataframe de Cartão de Crédito x Nuconta
        transactions_history_df = cls.creditCardTransactions = cls.creditCardTransactions.append(cls.debitTransactions).sort_values(by="time",ascending=False).reset_index().drop(columns=['index'])
        transactions_history_df['is_income'].fillna(False,inplace=True)
        transactions_history_df.fillna("NULL",inplace=True)
        cls.fullTransactionsHistory = transactions_history_df
        
    @classmethod
    def get_current_savings(cls):
        accBalance = int(cls.nu.get_account_balance() + cls.SELIC2022 + cls.ITAU + cls.NU_INVEST)
        logging.debug(f'Current Savings extracted: {accBalance}\n\tItau account = {cls.ITAU}\n\tNu Investments = {cls.NU_INVEST}\n\tSELCT July 2022 = {cls.SELIC2022}')
        cls.currentSavings = str(accBalance)
        #TestnuService().test_current_savings(cls.currentSavings)
    @classmethod
    def update_gsheet(cls):
        cls.gsheet.insert_values(cls.fullTransactionsHistory, cls.currentSavings, cls.currentDatetime)