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
        mapbox_style="open-street-map",
        height = 1000
    )
    
    # Exibir o mapa
    st.plotly_chart(fig)
    
    # Contar quantos valores NaN existem na coluna 'latitude' por município
    nan_por_municipio = df[df['latitude'].isna()].groupby('Municipio').size().reset_index(name='NaN_Latitude')
    
    # Contar o total de registros por município
    total_por_municipio = df.groupby('Municipio').size().reset_index(name='Total_Registros')
    
    # Unir os dois DataFrames
    resultado = pd.merge(nan_por_municipio, total_por_municipio, on='Municipio', how='right').fillna(0)
    
    # Calcular a porcentagem de valores NaN
    resultado['% NaN'] = round((resultado['NaN_Latitude'] / resultado['Total_Registros']) * 100)
    
    # Adicionar linha de total
    total_nan = resultado['NaN_Latitude'].sum()
    total_registros = resultado['Total_Registros'].sum()
    total_percentual = (total_nan / total_registros) * 100 if total_registros > 0 else 0
    
    linha_total = pd.DataFrame({
        'Municipio': ['TOTAL'],
        'NaN_Latitude': [total_nan],
        'Total_Registros': [total_registros],
        '% NaN': [total_percentual]
    })
    
    # Concatenar com o DataFrame original
    resultado = pd.concat([resultado, linha_total], ignore_index=True)

    # renomeando as coluans
    resultado.columns = ['Município','Não achados', 'Total notificações', 'Porcentagem']
    
    # Exibir o resultado
    st.dataframe(resultado, hide_index = True)

