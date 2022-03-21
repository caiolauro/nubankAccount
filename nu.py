from pynubank import Nubank, MockHttpClient
import json
import pandas as pd
from datetime import datetime
from delta import get_metrics
from gsheet import SpreadSheet
import re

gsheet = SpreadSheet()
current_datetime = datetime.now().strftime('%Y-%m-%d')
nu = Nubank()

with open("creds/credentials.json", "r", encoding="utf-8") as json_file:
    data = json.load(json_file)


fresh_token = nu.authenticate_with_cert(data["login"], data["pwd"], r"creds/cert.p12")

with open(r"creds/fresh_token", 'w') as token_file:
    token_file.write(fresh_token)

# Extrai compras feitas no cartão de crédito
credit_transactions = nu.get_card_statements()

df = pd.json_normalize(credit_transactions)

#Selecionando apenas colunas de interesse
credit_df = df[['description', 'category', 'amount', 'time', 'title','details.subcategory']]

'BillPaymentEvent'
# removendo caracteres indesejados da coluna de data da transação
credit_df['time'] = credit_df['time'].apply(lambda x: x.replace("Z","").replace("T"," "))

# Gerando colunas para diferentes granularidades de data a partir credit_df['time'].apply(lambda date: str(datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
credit_df.loc[:,'amount'] = credit_df['amount'] / 100
credit_df.loc[:,'hour'] = credit_df['time'].apply(lambda date: str(datetime.strptime(date, '%Y-%m-%d %H:%M:%S').hour))
credit_df.loc[:,'day'] = credit_df['time'].apply(lambda date: str(datetime.strptime(date, '%Y-%m-%d %H:%M:%S').day))
#credit_df.loc[:,'week_of_year'] = credit_df['time'].apply(lambda date: str(datetime.strptime(date, '%Y-%m-%d %H:%M:%S')))
#credit_df.loc[:,'week_day'] = credit_df['time'].apply(lambda date: str(datetime.strptime(date, '%Y-%m-%d %H:%M:%S').weekday))
credit_df.loc[:,'month'] = credit_df['time'].apply(lambda date: str(datetime.strptime(date, '%Y-%m-%d %H:%M:%S').month))
credit_df.loc[:,'year'] = credit_df['time'].apply(lambda date: str(datetime.strptime(date, '%Y-%m-%d %H:%M:%S').year))

# Extraindo transações Nuconta
account_statements = nu.get_account_statements()
# Criando dataframe 
nuconta_df = pd.DataFrame(account_statements).fillna("NULL")

# Criando coluna diferenciando o que é Entrada e Saída
nuconta_df.loc[:,'is_income'] = nuconta_df['title'].apply(lambda x: True if x.lower().__contains__("recebid") or  x.lower().__contains__("devolvid") else False)

# Selecionando apenas registros de Saída
#nuconta_df_2 = nuconta_df.where(((nuconta_df['is_income']==False)) & (nuconta_df['detail'].str.contains("Adyen") == False)).dropna()


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
#nuconta_df_2.loc[:,'week_of_year'] = nuconta_df_2['time'].apply(lambda date: str(datetime.strptime(date, "%Y-%m-%d").isocalendar().week))
#nuconta_df_2.loc[:,'week_day']  = nuconta_df_2['time'].apply(lambda date: str(datetime.strptime(date, "%Y-%m-%d").isocalendar().weekday))
nuconta_df_2.loc[:,'month'] = nuconta_df_2['time'].apply(lambda date: str(datetime.strptime(date, "%Y-%m-%d").month))
nuconta_df_2.loc[:,'year'] = nuconta_df_2['time'].apply(lambda date: str(datetime.strptime(date, "%Y-%m-%d").year))
nuconta_df_2.loc[:,'time'] = nuconta_df_2['time'] + ' 12:00:00'

# Label para Nuconta
nuconta_df_2.loc[:,'description'] = 'NULL'
nuconta_df_2.loc[:,'category'] = 'Nuconta'

# Merge do Dataframe de Cartão de Crédito x Nuconta
transactions_history_df = credit_df.append(nuconta_df_2).sort_values(by="time",ascending=False).reset_index().drop(columns=['index'])
transactions_history_df['is_income'].fillna(False,inplace=True)
transactions_history_df.fillna("NULL",inplace=True)

metrics = get_metrics(transactions_history_df, 'time','amount')

spend = metrics['acumm_spend_amount']
delta_percentual = metrics['percentual_delta']
period = metrics['period_info']
# somando valor que está investido na SELIC com retirada em JUL'22 + Conta Itaú + Ações Nubank
accBalance = nu.get_account_balance() + 7201.38 + 2600 + 600 #LU: 27/01/2022


gsheet.insert_values(df=transactions_history_df
                        ,accBalance=accBalance
                        ,spend=spend 
                        ,delta_percentual=delta_percentual
                        , period_of_time=period
                        , current_datetime=current_datetime)