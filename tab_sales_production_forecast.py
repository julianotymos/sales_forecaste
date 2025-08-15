import streamlit as st
from read_sales_production_forecast import read_sales_production_forecast
from datetime import datetime

# Para exibir imagens, você pode usar um dicionário que mapeia o nome do item para o caminho da imagem.
# Certifique-se de que as imagens estão em uma pasta acessível (por exemplo, 'images/').
# Este é um exemplo, substitua pelos caminhos reais das suas imagens.
ITEM_IMAGES = {
    'Morango': 'images/morango.png',
    'Kiwi': 'images/kiwi.png',
    'Uva': 'images/uva.png',
    'Brigadeiro': 'images/brigadeiro.png',
    'Beijinho': 'images/beijinho.png',
    'Cajuzinho': 'images/cajuzinho.png'
}

def tab_sales_production_forecast():
    """
    Exibe a aba de previsão de produção com informações visuais para o dia atual
    e uma tabela com os dados dos dias futuros.
    """
    #st.header("📋 Previsão de Produção")

    production_forecast_df = read_sales_production_forecast()

    if not production_forecast_df.empty:
        # Se houver mais de um registro, separamos o primeiro (hoje)
        # e o restante (dias futuros).
        today_forecast_df = production_forecast_df.head(1)
        future_forecast_df = production_forecast_df.iloc[1:]

        if not today_forecast_df.empty:
            forecast_row = today_forecast_df.iloc[0]
            
            st.markdown(f"**Previsão para o dia:** {forecast_row['Data'].strftime('%d/%m/%Y')}")

            # Exibe o faturamento de referência e temperatura para hoje
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Faturamento de Referência", f"R$ {forecast_row['Fat. de Referência']:.2f}")
            with col2:
                st.metric("Temperatura Média", f"{forecast_row['Temperatura']:.2f} °C")
                
            st.markdown("---")

            st.subheader("Itens a Produzir Hoje (g)")
            
            # Cria colunas para exibir os itens de forma visual para o dia de hoje
            cols = st.columns(3)
            item_names = ['Morango', 'Kiwi', 'Uva', 'Brigadeiro', 'Beijinho', 'Cajuzinho']
            
            for i, item in enumerate(item_names):
                with cols[i % 3]:
                    if item in ITEM_IMAGES:
                        try:
                            st.image(ITEM_IMAGES[item], caption=item, width=100)
                        except FileNotFoundError:
                            st.warning(f"⚠️ Imagem para {item} não encontrada.")
                            
                    st.markdown(f"### {forecast_row[item]:.2f}")

        # Se houver dados para dias futuros, exibe a tabela
        if not future_forecast_df.empty:
            st.markdown("---")
            st.subheader("Previsões para os Próximos Dias")
            
            # Converte a coluna 'Data' para o formato de exibição 'dd/mm/aaaa'
            #future_forecast_df['Data'] = pd.to_datetime(future_forecast_df['Data']).dt.strftime('%d/%m/%Y')
            
            st.dataframe(future_forecast_df.set_index('Data'))

    else:
        st.warning("⚠️ Não há dados de previsão de produção para hoje ou para os próximos dias. Por favor, verifique a base de dados.")