import streamlit as st
import pandas as pd
from psycopg2.extras import RealDictCursor
import datetime

from get_conection import get_connection

def read_sales_forecast_report(start_date, end_date):
    """
    Lê os dados de previsão e vendas realizadas do banco de dados e retorna 
    DataFrames processados, incluindo totais.
    """
    query = """
    SELECT
        DATE AS DATE,
        MAX(DAY_OF_WEEK) AS DAY_OF_WEEK,
        ROUND(AVG(TEMPERATURE)::NUMERIC, 2) AS TEMPERATURE,
        ROUND(SUM(FORECAST_REVENUE)::NUMERIC, 2) AS FORECAST_REVENUE,
        ROUND(COALESCE(SUM(REALIZED_REVENUE), 0)::NUMERIC, 2) AS REALIZED_REVENUE,
        ROUND(SUM(STORE_SALES_FORECAST)::NUMERIC, 2) AS STORE_SALES_FORECAST,
        ROUND(COALESCE(SUM(STORE_SALES_REALIZED), 0)::NUMERIC, 2) AS STORE_SALES_REALIZED,
        ROUND(SUM(DELIVERY_SALES_FORECAST)::NUMERIC, 2) AS DELIVERY_SALES_FORECAST,
        ROUND(COALESCE(SUM(DELIVERY_SALES_REALIZED), 0)::NUMERIC, 2) AS DELIVERY_SALES_REALIZED
    FROM
        SALES_FORECAST sf
    WHERE
        sf.DATE >= %s
        AND sf.DATE <= %s
    GROUP BY
        DATE
    ORDER BY
        DATE desc;
    """
    
    # Mapeamento de colunas para nomes mais amigáveis para o Streamlit
    column_rename_map = {
        'date': 'Data',
        'day_of_week': 'Dia da Semana',
        'temperature': 'Temperatura',
        'forecast_revenue': 'Previsão de Faturamento',
        'realized_revenue': 'Faturamento Realizado',
        'store_sales_forecast': 'Previsão Vendas Loja',
        'store_sales_realized': 'Vendas Realizadas Loja',
        'delivery_sales_forecast': 'Previsão Vendas Delivery',
        'delivery_sales_realized': 'Vendas Realizadas Delivery'
    }

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (start_date, end_date))
            data = cursor.fetchall()
            
            # Obtém os nomes das colunas do cursor para criar o DataFrame
            col_names = [desc[0] for desc in cursor.description]
            df = pd.DataFrame(data, columns=col_names)
            
            if not df.empty:
                # Conversão de tipos para garantir que sejam numéricos, exceto as colunas de texto
                numeric_cols = [col for col in col_names if col not in ['date', 'day_of_week']]
                for col in numeric_cols:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                
                # --- LÓGICA CORRIGIDA PARA CÁLCULO DE TOTAIS ---
                
                # Cria um dicionário com os totais de cada coluna numérica
                # A temperatura deve ser a média, não a soma
                total_row_data = {
                    'temperature': df['temperature'].mean(),
                    'forecast_revenue': df['forecast_revenue'].sum(),
                    'realized_revenue': df['realized_revenue'].sum(),
                    'store_sales_forecast': df['store_sales_forecast'].sum(),
                    'store_sales_realized': df['store_sales_realized'].sum(),
                    'delivery_sales_forecast': df['delivery_sales_forecast'].sum(),
                    'delivery_sales_realized': df['delivery_sales_realized'].sum(),
                }
                
                # Adicionando 'day_of_week' e 'date' ao dicionário para evitar key_error
                total_row_data['date'] = 'Total'
                total_row_data['day_of_week'] = '-'
                
                # Cria o DataFrame de totais
                total_row_df = pd.DataFrame([total_row_data])
                
                # Reordena as colunas para corresponder ao DataFrame original
                total_row_df = total_row_df[col_names]

                # Renomeia as colunas dos dois DataFrames
                df.rename(columns=column_rename_map, inplace=True)
                total_row_df.rename(columns=column_rename_map, inplace=True)
                
                # Retorna os dois DataFrames processados
                return df, total_row_df
            
            # Retorna DataFrames vazios caso não haja dados
            empty_df = pd.DataFrame(columns=list(column_rename_map.values()))
            return empty_df, empty_df