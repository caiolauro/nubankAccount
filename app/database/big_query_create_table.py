from google.cloud import bigquery
import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="/mnt/c/users/caio.lauro/Documents/personal_projects/NuBankAPI/creds/credentials.json"
client = bigquery.Client()

# Perform a query.
QUERY1 = (
    """CREATE SCHEMA PYNUBANK;"""
    )
QUERY = (
    """CREATE TABLE PYNUBANK.TRANSACTIONS_HISTORY
        (  merchant string
        , source string
        , amount numeric
        , datetime timestamp
        , category string
        , payment_method string
        , hour integer
        , day integer
        , month integer
        , year integer
        , is_income boolean
        , details string
        );"""
    )
query_job = client.query(QUERY)  # API request
result = query_job.result()