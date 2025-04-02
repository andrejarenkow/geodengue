import pandas as pd
import plotly.express as px
import streamlit as st

# Título do painel
st.title("Mapa de Endereços com Coordenadas")

# Upload do arquivo CSV
uploaded_file = st.file_uploader("Envie um arquivo CSV", type=["csv"])

if uploaded_file is not None:
    # Carregar o arquivo CSV
    df = pd.read_csv(uploaded_file)
    
    # Criar o mapa
    fig = px.scatter_mapbox(
        df,
        lat="latitude",
        lon="longitude",
        hover_name=df.columns[0],  # Nome da primeira coluna para exibição no hover
        zoom=10,
        mapbox_style="open-street-map"
    )
    
    # Exibir o mapa
    st.plotly_chart(fig)
    
    # Exibir a tabela com os dados
    st.dataframe(df)
