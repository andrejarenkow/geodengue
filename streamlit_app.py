import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_plotly_events import plotly_events

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
    df = pd.read_csv(uploaded_file)

    df['CLASSI_FIN'] = df['CLASSI_FIN'].fillna('Em investigação').astype(str)
    df["DT_SIN_PRI"] = pd.to_datetime(df["DT_SIN_PRI"], errors="coerce")
    df = df[df['DT_SIN_PRI'].dt.year == 2025]
    df["Semana_Epidemiologica"] = df["DT_SIN_PRI"].dt.strftime('%Y-%U')
    df = df.sort_values(by="DT_SIN_PRI")

    dicionario_classifi = {
        '5.0': 'Descartado',
        '10.0': 'Dengue',
        '11.0': 'Dengue com sinais de alarme',
        '12.0': 'Dengue grave',
        '13.0': 'Chikungunya',
        '8.0': 'Fechado pelo sistema'
    }
    df['CLASSI_FIN'] = df['CLASSI_FIN'].replace(dicionario_classifi)

    st.sidebar.header("Filtro de Município")
    municipio = st.sidebar.selectbox(label='Selecione um município:', options=sorted(df['Municipio'].unique()))
    aplicar_filtro = st.sidebar.button("Aplicar Filtro")

    mapa_calor = st.sidebar.checkbox("Exibir como mapa de calor")
    usar_animacao = st.sidebar.checkbox("Ativar animação cumulativa")

    lat_center = (df['latitude'].max() + df['latitude'].min()) / 2
    lon_center = (df['longitude'].max() + df['longitude'].min()) / 2
    zoom_ini = 5.5

    if aplicar_filtro:
        df = df[df['Municipio'] == municipio]
        lat_center = (df['latitude'].max() + df['latitude'].min()) / 2
        lon_center = (df['longitude'].max() + df['longitude'].min()) / 2
        zoom_ini = 10

    if usar_animacao:
        semanas_unicas = sorted(df["Semana_Epidemiologica"].unique())
        df_cumulativo = pd.DataFrame()
        for semana in semanas_unicas:
            df_temp = df[df["Semana_Epidemiologica"] <= semana].copy()
            df_temp["Semana_Cumulativa"] = semana
            df_cumulativo = pd.concat([df_cumulativo, df_temp])
        df = df_cumulativo

    params = {
        "lat": "latitude",
        "lon": "longitude",
        "hover_name": "endereco",
        "hover_data": df.columns,
        "zoom": zoom_ini,
        "mapbox_style": "open-street-map",
        "center": {"lat": lat_center, "lon": lon_center},
        "height": 800,
        "width": 800,
        "opacity": 0.8,
        "color": "CLASSI_FIN",
        "color_discrete_map": {
            "Descartado": "grey",
            "Dengue": "orange",
            "Dengue com sinais de alarme": "red",
            "Dengue grave": "black",
            "Chikungunya": "blue",
            "Fechado pelo sistema": "green",
            "Em investigação": "purple"
        }
    }
    if usar_animacao:
        params["animation_frame"] = "Semana_Cumulativa"

    fig = px.scatter_mapbox(df, **params)

    # Captura de clique
    selected_points = plotly_events(
        fig,
        click_event=True,
        hover_event=False,
        select_event=False,
        override_height=800,
        override_width='100%'
    )

    st.subheader("Editar coordenadas")
    if selected_points:
        ponto_clicado = selected_points[0]
        st.info(f"Coordenada selecionada: lat={ponto_clicado['y']}, lon={ponto_clicado['x']}")

        df_filtrado = df[
            (df['latitude'] == ponto_clicado['y']) &
            (df['longitude'] == ponto_clicado['x'])
        ]
        df_editado = st.data_editor(df_filtrado, num_rows="dynamic")

        # Substituir apenas os registros que foram editados
        for idx in df_editado.index:
            original_idx = df[df['latitude'] == ponto_clicado['y']].index
            df.loc[original_idx, 'latitude'] = df_editado.loc[idx, 'latitude']
            df.loc[original_idx, 'longitude'] = df_editado.loc[idx, 'longitude']

    else:
        df_editado = st.data_editor(df, num_rows="dynamic")
        df.update(df_editado)

    st.subheader("Mapa atualizado")
    fig_atualizado = px.scatter_mapbox(df, **params)
    st.plotly_chart(fig_atualizado, use_container_width=True, config={"scrollZoom": True})

    nan_por_municipio = df[df['latitude'].isna()].groupby('Municipio').size().reset_index(name='NaN_Latitude')
    total_por_municipio = df.groupby('Municipio').size().reset_index(name='Total_Registros')
    resultado = pd.merge(nan_por_municipio, total_por_municipio, on='Municipio', how='right').fillna(0)
    resultado['% NaN'] = round((resultado['NaN_Latitude'] / resultado['Total_Registros']) * 100)
    total_nan = resultado['NaN_Latitude'].sum()
    total_registros = resultado['Total_Registros'].sum()
    total_percentual = (total_nan / total_registros) * 100 if total_registros > 0 else 0
    linha_total = pd.DataFrame({
        'Municipio': ['TOTAL'],
        'NaN_Latitude': [total_nan],
        'Total_Registros': [total_registros],
        '% NaN': [total_percentual]
    })
    resultado = pd.concat([resultado, linha_total], ignore_index=True)
    resultado.columns = ['Município', 'Não achados', 'Total notificações', 'Porcentagem']
    st.dataframe(resultado, hide_index=True)
