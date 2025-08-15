import datetime
import random
import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
from read_process_last_run import read_process_last_run
from datetime import datetime, timedelta
from typing import List
from tab_sales_forecast_report import tab_sales_forecast_report
from tab_sales_production_forecast import tab_sales_production_forecast  # Importe a nova função

# Show app title and description.
# --- Início da Aplicação Streamlit ---

st.set_page_config(
    page_title="Dashboard de Previsão de Vendas",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📊 Previsão de Vendas")
#st.markdown("Análise comparativa entre o faturamento previsto e o faturamento realizado.")

# --- Barra Lateral para Filtros e Status ---
st.sidebar.header("🗓️ Período de Análise")
today = datetime.now().date()

start_of_week = today - timedelta(days=today.weekday())
end_of_week = start_of_week + timedelta(days=6)

start_date = st.sidebar.date_input("Data Inicial", start_of_week)
end_date = st.sidebar.date_input("Data Final", end_of_week)

if start_date > end_date:
    st.sidebar.error("⚠️ Erro: A data inicial não pode ser posterior à data final.")
else:
    # --- Criação da Aba Única ---
    tab_forecast, tab_production = st.tabs(["Previsão de Vendas", "Previsão de Produção"])

    with tab_forecast:
        tab_sales_forecast_report(start_date, end_date)

    with tab_production:
        # A segunda aba usa a nova função, que não precisa de parâmetros
        tab_sales_production_forecast() 

    # --- Status de Processamento na Barra Lateral (comum para a aba) ---
    st.sidebar.markdown("---")
    st.sidebar.header("🔄 Status de Processamento")
    last_run_df = read_process_last_run(["SALES_FORECAST_PROCESS"])
    if not last_run_df.empty:
        for index, row in last_run_df.iterrows():
            st.sidebar.info(f"**{row['name']}**\nÚltima atualização: {row['last_run_date'].strftime('%d/%m/%Y %H:%M:%S')}")
    else:
        st.sidebar.warning("Nenhum dado de status encontrado.")