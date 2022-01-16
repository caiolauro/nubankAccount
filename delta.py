from datetime import datetime
from datetime import timedelta

def get_metrics(df, datetime_column_name:str, amount_column_name:str):
    
    to_datetime = lambda date: datetime.strptime(date,'%Y-%m-%d %H:%M:%S')
    # Cálculo das datas limites
    diff_7 = (datetime.now() - timedelta(days=7))
    diff_15 = (datetime.now() - timedelta(days=15))
    diff_30 = (datetime.now() - timedelta(days=30))
    diff_60 = (datetime.now() - timedelta(days=60))



    D7 = "From " + datetime.strftime(diff_7, "%B %dth")
    D15 = "From " + datetime.strftime(diff_15, "%B %dth")
    D30 = "From " + datetime.strftime(diff_30, "%B %dth")


    # Cálculo de gastos dos últimos 7, 15 e 30 dias

    last7D = df.where(df[datetime_column_name].apply(to_datetime) > diff_7).dropna()[amount_column_name].sum()
    last7D_2 = df.where((df[datetime_column_name].apply(to_datetime) < diff_7) & (df[datetime_column_name].apply(to_datetime) > diff_15)).dropna()[amount_column_name].sum()
    delta_7D = ((last7D/last7D_2) - 1)


    last15D = df.where(df[datetime_column_name].apply(to_datetime) > diff_15).dropna()[amount_column_name].sum()
    last15D_2 = df.where((df[datetime_column_name].apply(to_datetime) < diff_15) & (df[datetime_column_name].apply(to_datetime) > diff_30)).dropna()[amount_column_name].sum()
    delta_15D = ((last15D/last15D_2) - 1)

    last30D = df.where(df[datetime_column_name].apply(to_datetime) > diff_30).dropna()[amount_column_name].sum()
    last30D_2 = df.where((df[datetime_column_name].apply(to_datetime) < diff_30) & (df[datetime_column_name].apply(to_datetime) > diff_60)).dropna()[amount_column_name].sum()
    delta_30D = ((last30D/last30D_2) - 1)
    
    return dict( 
                    acumm_spend_amount = [last7D,last15D,last30D],
                    percentual_delta = [delta_7D,delta_15D,delta_30D],
                    period_info = [[D7],[D15],[D30]]
                )