import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff

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

# Sidebar - Upload do CSV e filtros
st.sidebar.title("Configurações")

# Upload do arquivo CSV na sidebar
uploaded_file = st.sidebar.file_uploader("Envie seu arquivo CSV", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    # Checa colunas essenciais
    if "latitude" not in df.columns or "longitude" not in df.columns:
        st.error("O CSV precisa conter colunas chamadas 'latitude' e 'longitude'.")
        st.stop()

    # Colunas opcionais com preenchimento padrão
    if "endereco" not in df.columns:
        df["endereco"] = "Endereço não informado"
    if "CLASSI_FIN" not in df.columns:
        df["CLASSI_FIN"] = "Classificação não informada"
    if "municipio" not in df.columns:
        df["municipio"] = "Município não informado"

    # Filtro de município na sidebar
    municipios = sorted(df["municipio"].dropna().unique())
    municipio_selecionado = st.sidebar.selectbox("Filtrar por município", ["Todos"] + municipios)

    if municipio_selecionado != "Todos":
        df = df[df["municipio"] == municipio_selecionado]

    # Centralização do mapa
    lat_center = df["latitude"].mean()
    lon_center = df["longitude"].mean()
    zoom_ini = 8

    # Checkboxes para escolher o tipo de mapa
    usar_heatmap = st.sidebar.checkbox("Usar mapa de calor")
    usar_hexbin = st.sidebar.checkbox("Usar mapa hexbin")

    if usar_heatmap and usar_hexbin:
        st.sidebar.warning("Escolha apenas um tipo de visualização.")
        st.stop()

    # Token do Mapbox
    try:
        mapbox_token = open(".mapbox_token").read()
        px.set_mapbox_access_token(mapbox_token)
    except:
        st.warning("Token do Mapbox não encontrado. Coloque seu token no arquivo `.mapbox_token`.")
        mapbox_token = None

    # Visualizações
    if usar_heatmap:
        fig = px.density_mapbox(
            df,
            lat="latitude",
            lon="longitude",
            radius=15,
            mapbox_style="open-street-map",
            center={'lat': lat_center, 'lon': lon_center},
            zoom=zoom_ini,
            height=800,
            width=800
        )

    elif usar_hexbin and mapbox_token:
        fig = ff.create_hexbin_mapbox(
            data_frame=df,
            lat="latitude",
            lon="longitude",
            nx_hexagon=20,
            opacity=0.6,
            labels={"color": "Número de notificações"},
            min_count=1,
            color_continuous_scale="Viridis",
            show_original_data=True,
            original_data_marker=dict(size=4, opacity=0.4, color="deeppink"),
            center={"lat": lat_center, "lon": lon_center},
            zoom=zoom_ini,
            height=800,
            width=800
        )

    else:
        fig = px.scatter_mapbox(
            df,
            lat="latitude",
            lon="longitude",
            hover_name="endereco",
            hover_data=df.columns,
            zoom=zoom_ini,
            mapbox_style="open-street-map",
            center={"lat": lat_center, "lon": lon_center},
            height=800,
            width=800,
            opacity=0.8,
            color="CLASSI_FIN",
            color_discrete_map={
                "Descartado": "grey",
                "Dengue": "orange",
                "Dengue com sinais de alarme": "red",
                "Dengue grave": "black",
                "Chikungunya": "blue",
                "Fechado pelo sistema": "green",
                "Em investigação": "purple",
                "Classificação não informada": "lightgrey"
            }
        )

    st.plotly_chart(fig, use_container_width=True, config={"scrollZoom": True})

else:
    st.sidebar.info("Envie um arquivo CSV para começar.")
    st.info("O mapa será exibido aqui após o envio do CSV.")
