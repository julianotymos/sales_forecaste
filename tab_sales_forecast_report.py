import streamlit as st
from read_sales_forecast_report import read_sales_forecast_report
from datetime import datetime, timedelta
import altair as alt
import numpy as np # Importe a biblioteca NumPy para usar np.nan

def tab_sales_forecast_report(start_date, end_date):
    """
    Exibe o conteúdo da aba "Previsão de Vendas",
    incluindo métricas e análise de faturamento previsto vs. realizado.
    """
    #st.header("Análise de Previsão de Vendas")

    daily_report_df, total_report_df = read_sales_forecast_report(start_date, end_date)
    
    if not total_report_df.empty:
        total_row = total_report_df.iloc[0]
        
        # Exibição das métricas totais
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Fat. Realizado Total", f"{total_row['Faturamento Realizado']:.2f}", delta=f"{(total_row['Faturamento Realizado'] - total_row['Previsão de Faturamento']):.2f}")
            
        with col2:
            st.metric("Fat. Previsto Total", f"{total_row['Previsão de Faturamento']:.2f} ")

        with col3:
            st.metric("Fat. Realizadas Loja", f"{total_row['Vendas Realizadas Loja']:.2f}", delta=f"{(total_row['Vendas Realizadas Loja'] - total_row['Previsão Vendas Loja']):.2f}")
            
        with col4:
            st.metric("Fat. Previsto Loja", f"{total_row['Previsão Vendas Loja']:.2f} ")
        with col5:
            st.metric("Temperatura Média", f"{total_row['Temperatura']:.2f} °C")
            
        st.markdown("---")
        
        # Novas colunas para as métricas de delivery
        col_del1, col_del2 , col_vazio1, col_vazio2, col_vazio3 = st.columns(5)
        
        with col_del1:
            st.metric("Fat. Realizado Delivery", f"{total_row['Vendas Realizadas Delivery']:.2f}", delta=f"{(total_row['Vendas Realizadas Delivery'] - total_row['Previsão Vendas Delivery']):.2f}")

        with col_del2:
            st.metric("Fat. Previsto Delivery", f"{total_row['Previsão Vendas Delivery']:.2f}")


        st.markdown("---")
        

# Gráfico comparando todas as métricas de faturamento
        st.subheader("Faturamento Previsto vs. Realizado (Diário) por Canal")

        # Preparando o DataFrame para o gráfico
        df_long = daily_report_df.melt(
            id_vars=['Data', 'Dia da Semana'],
            value_vars=[
                'Previsão de Faturamento', 
                'Faturamento Realizado', 
                'Previsão Vendas Loja', 
                'Vendas Realizadas Loja',
                'Previsão Vendas Delivery',
                'Vendas Realizadas Delivery'
            ],
            var_name='Tipo de Faturamento',
            value_name='Valor'
        )
        mapeamento_nomes = {
        'Previsão de Faturamento': 'Previsão Total',
        'Faturamento Realizado': 'Realizado Total',
        'Previsão Vendas Loja': 'Previsão Loja',
        'Vendas Realizadas Loja': 'Realizado Loja',
        'Previsão Vendas Delivery': 'Previsão Delivery',
        'Vendas Realizadas Delivery': 'Realizado Delivery'
        }

        df_long['Tipo de Faturamento'] = df_long['Tipo de Faturamento'].replace(mapeamento_nomes)

        # AQUI É A MUDANÇA: Substitua os valores zero por NaN para que não sejam exibidos no gráfico
        df_long['Valor'] = df_long['Valor'].replace(0, np.nan)
        chart = alt.Chart(df_long).mark_line(point=True).encode(
            x=alt.X('Data:T', title=None, axis=alt.Axis(format="%d/%m/%Y")),
            y=alt.Y('Valor:Q', title=None, axis=alt.Axis(format='.2f')),
            color=alt.Color('Tipo de Faturamento:N', title='Tipo de Faturamento', legend=alt.Legend(
                orient="bottom", 
                direction="horizontal",
                columns=2
            )),
            tooltip=[
                alt.Tooltip('Data:T', title=None, format="%d/%m/%Y"),
                alt.Tooltip('Tipo de Faturamento:N'),
                alt.Tooltip('Valor:Q', title=None, format=".2f")
            ]
        ).properties(
            title="Comparativo de Faturamento Diário por Canal"
        ).interactive()

        st.altair_chart(chart, use_container_width=True)
        
        st.markdown("---")
        
        st.subheader("Tabela de Dados Detalhada")
        st.dataframe(daily_report_df.set_index('Data'))
        
    else:
        st.warning("⚠️ Não há dados de previsão de vendas para o período selecionado. Por favor, ajuste o filtro de datas.")