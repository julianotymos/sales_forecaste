import streamlit as st
import pandas as pd
from psycopg2.extras import RealDictCursor
import datetime

from get_conection import get_connection

def read_sales_forecast_by_date(day_of_week='Domingo', time='12:00:00'):
    """
    Lê os dados de previsão de produção e faturamento do banco de dados
    filtrando por dia da semana e horário específicos.
    Retorna um DataFrame processado com os dados.
    """
    
    query = f"""
    SELECT 
        wd.weather_date AS weather_date,
        wd.day_of_week AS day_of_week,
        WD.TIME || ':00' AS time,
        WD.TEMPERATURE AS temperature,
        SF.FORECAST_REVENUE,
        SF.REALIZED_REVENUE,
        SF.STORE_SALES_REALIZED,
        SF.STORE_SALES_FORECAST,
        SF.DELIVERY_SALES_REALIZED,
        SF.DELIVERY_SALES_FORECAST
    FROM WEATHER_DATA wd
    INNER JOIN sales_forecast SF 
        ON SF.DATE = WD.weather_date 
        AND (WD.TIME || ':00')::time = SF.TIME
    LEFT JOIN WEATHER_CONDITIONS WC
        ON WC.DESCRIPTION = WD.DESCRIPTION
    WHERE 1=1
        AND SF.DAY_OF_WEEK = '{day_of_week}'
        AND SF.TIME = '{time}'
    ORDER BY wd.weather_date ASC;
    """

    # Mapeamento de colunas para nomes mais amigáveis para o Streamlit
    column_rename_map = {
        'weather_date': 'Data',
        'day_of_week': 'Dia da Semana',
        'time': 'Hora',
        'temperature': 'Temperatura',
        'forecast_revenue': 'Previsão Faturamento',
        'realized_revenue': 'Faturamento Realizado',
        'store_sales_realized': 'Faturamento Loja Realizado',
        'store_sales_forecast': 'Faturamento Loja Previsto',
        'delivery_sales_realized': 'Faturamento Delivery Realizado',
        'delivery_sales_forecast': 'Faturamento Delivery Previsto'
    }

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query)
            data = cursor.fetchall()
            
            col_names = [desc[0] for desc in cursor.description]
            df = pd.DataFrame(data, columns=col_names)
            
            if not df.empty:
                # Conversão de tipos para garantir que sejam numéricos, exceto as colunas de texto
                numeric_cols = [col for col in col_names if col not in ['weather_date', 'day_of_week', 'time']]
                for col in numeric_cols:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                
                # Renomeia as colunas do DataFrame
                df.rename(columns=column_rename_map, inplace=True)
                
                return df
            
            # Retorna um DataFrame vazio caso não haja dados
            return pd.DataFrame(columns=list(column_rename_map.values()))
#df = read_sales_forecast(day_of_week='Segunda', time='13:00:00' )
#print(df)