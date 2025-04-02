import pandas as pd
import plotly.express as px
import streamlit as st

# Configurações da página
st.set_page_config(
    page_title="Geodengue",
    page_icon=":bug:",
    layout="wide",
    initial_sidebar_state='expanded'
)

col1, col2, col3 = st.columns([1, 4, 1])

col1.image('https://github.com/andrejarenkow/csv/blob/master/logo_cevs%20(2).png?raw=true', width=100)
col2.header('Coordenadas Notificações Dengue')
col3.image('https://github.com/andrejarenkow/csv/blob/master/logo_estado%20(3)%20(1).png?raw=true', width=150)

# Sidebar para upload do arquivo
st.sidebar.header("Upload do Arquivo")
uploaded_file = st.sidebar.file_uploader("Envie um arquivo CSV", type=["csv"])

if uploaded_file is not None:
    # Carregar o arquivo CSV
    df = pd.read_csv(uploaded_file)

    # Criando filtro de município na sidebar
    st.sidebar.header("Filtro de Município")
    municipio = st.sidebar.selectbox(label='Selecione um município:', options=df['Municipio'].unique())
    aplicar_filtro = st.sidebar.button("Aplicar Filtro")

    # Centro do mapa
    lat_center = (df['latitude'].max() + df['latitude'].min()) / 2
    lon_center = (df['longitude'].max() + df['longitude'].min()) / 2
    zoom_ini = 5.5
    
    # Aplicar o filtro apenas quando o botão for clicado
    if aplicar_filtro:
        df = df[df['Municipio'] == municipio]
        # Centro do mapa
        lat_center = (df['latitude'].max() + df['latitude'].min()) / 2
        lon_center = (df['longitude'].max() + df['longitude'].min()) / 2
        zoom_ini = 10

    # Criar o mapa
    fig = px.scatter_mapbox(
        df,
        lat="latitude",
        lon="longitude",
        hover_name=df.columns[0],  # Nome da primeira coluna para exibição no hover
        zoom=zom_ini,
        mapbox_style="open-street-map",
        center={'lat': lat_center, 'lon': lon_center},
        height=800,
        width=800
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

    # Renomeando as colunas
    resultado.columns = ['Município', 'Não achados', 'Total notificações', 'Porcentagem']

    # Exibir o resultado
    st.dataframe(resultado, hide_index=True)
