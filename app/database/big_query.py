from google.cloud import bigquery
import os

class BigQuery:
    credentials_path = "/mnt/c/users/caio.lauro/Documents/personal_projects/NuBankAPI/creds/credentials.json"
    client = None
    def __init__(self) -> None:
        pass
    @classmethod
    def initialize(cls):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=cls.credentials_path
        client = bigquery.Client()
        cls.client = client
    def insert_values():
        pass