import streamlit as st
from read_sales_forecast_by_date import read_sales_forecast_by_date
import pandas as pd
import plotly.express as px
import numpy as np

def tab_analysis_date():
    """
    Exibe a aba "Previsão de Produção" mostrando métricas e gráfico
    de faturamento vs temperatura com linha de tendência, seleção de dia e hora.
    """
    st.header("Previsão de Produção - Análise por Dia e Hora")

    # Seleção do dia da semana
    dias_da_semana = ['Domingo', 'Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado']
    day_of_week = st.selectbox("Selecione o Dia da Semana", dias_da_semana, index=0)

    # Seleção da hora (11:00 até 21:00)
    horas = [f"{h:02d}:00:00" for h in range(11, 22)]
    time = st.selectbox("Selecione a Hora", horas, index=1)

    st.markdown(f"### Dados para {day_of_week} às {time}")

    # Leitura dos dados
    df = read_sales_forecast_by_date(day_of_week=day_of_week, time=time)

    if not df.empty:
        df['Faturamento Total'] = df['Faturamento Loja Realizado'] + df['Faturamento Delivery Realizado']

        # Métricas principais
        total_row = df.iloc[0]
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Faturamento Total", f"{total_row['Faturamento Total']:.2f}")
        with col2:
            st.metric("Previsão Total", f"{total_row['Previsão Faturamento']:.2f}")
        with col3:
            st.metric("Temperatura", f"{total_row['Temperatura']:.2f} °C")

        st.markdown("---")

        # Seleção de tipos de faturamento para o gráfico
        opcoes_faturamento = [
            'Faturamento Total',
            'Faturamento Loja Realizado',
            'Faturamento Delivery Realizado',
            'Previsão Faturamento',
            'Faturamento Loja Previsto',
            'Faturamento Delivery Previsto'
        ]
        tipos_selecionados = st.multiselect(
            "Selecione os Tipos de Faturamento para o Gráfico",
            options=opcoes_faturamento,
            default=['Faturamento Total', 'Previsão Faturamento']
        )

        if tipos_selecionados:
            df_long = df.melt(
                id_vars=['Data', 'Temperatura'],
                value_vars=tipos_selecionados,
                var_name='Tipo de Faturamento',
                value_name='Valor'
            )

            # --- Gráfico de dispersão com linha de tendência ---
            fig = px.scatter(
                df_long,
                x='Temperatura',
                y='Valor',
                color='Tipo de Faturamento',
                trendline="ols",  # Regressão linear
                trendline_scope="overall",  # linha de tendência global
                hover_data=['Data']
            )

            fig.update_layout(
                title=f"Tendência de Faturamento por Temperatura - {day_of_week} {time}",
                xaxis_title="Temperatura (°C)",
                yaxis_title="Faturamento",
                legend_title="Tipo de Faturamento"
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("⚠️ Selecione ao menos um tipo de faturamento para exibir o gráfico.")

        st.markdown("---")
        st.subheader("Tabela Detalhada")
        st.dataframe(df.set_index('Data'))

    else:
        st.warning("⚠️ Não há dados para o dia/hora selecionados.")
