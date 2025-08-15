import streamlit as st
import pandas as pd
from psycopg2.extras import RealDictCursor
import datetime

from get_conection import get_connection

def read_sales_production_forecast():
    """
    Lê os dados de previsão de produção do banco de dados para a data atual.
    Retorna um DataFrame processado com os dados.
    """
    # A data de hoje como string no formato 'YYYY-MM-DD'
    today = datetime.date.today().strftime('%Y-%m-%d')
    
    query = f"""
    SELECT
        DATE AS DATE,
        MAX(DAY_OF_WEEK) AS DAY_OF_WEEK,
        ROUND(AVG(TEMPERATURE)::NUMERIC, 2) AS TEMPERATURE,
        
        ROUND(SUM( STORE_SALES_FORECAST + DELIVERY_SALES_FORECAST/2)::NUMERIC, 2) AS FAT_REF , 
        ROUND(SUM( (STORE_SALES_FORECAST + DELIVERY_SALES_FORECAST/2)* 0.5614035088)::NUMERIC, 2) AS MORANGO ,  
        ROUND(SUM( (STORE_SALES_FORECAST + DELIVERY_SALES_FORECAST/2)* 0.1403508772)::NUMERIC, 2) AS KIWI ,  
        ROUND(SUM( (STORE_SALES_FORECAST + DELIVERY_SALES_FORECAST/2)* 0.08771929825)::NUMERIC, 2) AS UVA ,  
        ROUND(SUM( (STORE_SALES_FORECAST + DELIVERY_SALES_FORECAST/2)* 0.2105263158)::NUMERIC, 2) AS BRIGADEIRO ,  
        ROUND(SUM( (STORE_SALES_FORECAST + DELIVERY_SALES_FORECAST/2)* 0.1403508772)::NUMERIC, 2) AS BEIJINHO ,  
        ROUND(SUM( (STORE_SALES_FORECAST + DELIVERY_SALES_FORECAST/2)* 0.8771929825)::NUMERIC, 2) AS CAJUZINHO   

    FROM
        SALES_FORECAST sf
    WHERE
        sf.DATE >= '{today}'
    GROUP BY
        DATE
    ORDER BY
        DATE ASC;
    """
    
    # Mapeamento de colunas para nomes mais amigáveis para o Streamlit
    column_rename_map = {
        'date': 'Data',
        'day_of_week': 'Dia da Semana',
        'temperature': 'Temperatura',
        'fat_ref': 'Fat. de Referência',
        'morango': 'Morango',
        'kiwi': 'Kiwi',
        'uva': 'Uva',
        'brigadeiro': 'Brigadeiro',
        'beijinho': 'Beijinho',
        'cajuzinho': 'Cajuzinho'
    }

    with get_connection() as conn:
        with conn.cursor() as cursor:
            # Não passamos parâmetros para o execute, pois a data já está na string da query
            cursor.execute(query)
            data = cursor.fetchall()
            
            col_names = [desc[0] for desc in cursor.description]
            df = pd.DataFrame(data, columns=col_names)
            
            if not df.empty:
                # Conversão de tipos para garantir que sejam numéricos, exceto as colunas de texto
                numeric_cols = [col for col in col_names if col not in ['date', 'day_of_week']]
                for col in numeric_cols:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                
                # Renomeia as colunas do DataFrame
                df.rename(columns=column_rename_map, inplace=True)
                
                # Retorna apenas o DataFrame
                return df
            
            # Retorna um DataFrame vazio caso não haja dados para a data atual
            return pd.DataFrame(columns=list(column_rename_map.values()))