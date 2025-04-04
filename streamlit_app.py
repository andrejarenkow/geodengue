import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff

st.title("Mapa Interativo de Notificações")

# Upload de arquivo CSV
uploaded_file = st.file_uploader("Envie seu arquivo CSV", type=["csv"])
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    # Confirma existência das colunas necessárias
    if "latitude" not in df.columns or "longitude" not in df.columns:
        st.error("O arquivo CSV precisa conter colunas chamadas 'latitude' e 'longitude'.")
        st.stop()

    # Preenche dados simulados para exemplo, caso outras colunas faltem
    if "endereco" not in df.columns:
        df["endereco"] = "Endereço não informado"
    if "CLASSI_FIN" not in df.columns:
        df["CLASSI_FIN"] = "Classificação não informada"

    # Centralização do mapa
    lat_center = df["latitude"].mean()
    lon_center = df["longitude"].mean()
    zoom_ini = 8

    # Sidebar de opções
    st.sidebar.title("Opções de visualização")
    usar_heatmap = st.sidebar.checkbox("Usar mapa de calor")
    usar_hexbin = st.sidebar.checkbox("Usar mapa hexbin")

    if usar_heatmap and usar_hexbin:
        st.sidebar.warning("Escolha apenas um tipo de visualização: Heatmap ou Hexbin.")
        st.stop()

    # Token do Mapbox
    #try:
        #mapbox_token = open(".mapbox_token").read()
        #px.set_mapbox_access_token(mapbox_token)
    #except:
    #    st.warning("Token do Mapbox não encontrado. Coloque seu token no arquivo `.mapbox_token`.")
    #    mapbox_token = None

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

    elif usar_hexbin:
        fig = ff.create_hexbin_mapbox(
            data_frame=df,
            lat="latitude",
            lon="longitude",
            nx_hexagon=20,
            opacity=0.6,
            labels={"color": "Número de notificações"},
            min_count=1,
            color_continuous_scale="Viridis",
            map_style="open-street-map",
            show_original_data=True,
            original_data_marker=dict(size=4, opacity=0.4, color="deeppink"),
            center={"lat": lat_center, "lon": lon_center},
            zoom=zoom_ini,
            height=800,
            width=800
        )

    else:
        fig = px.scatter_map(
            df,
            lat="latitude",
            lon="longitude",
            hover_name="endereco",
            hover_data=df.columns,
            zoom=zoom_ini,
            map_style="open-street-map",
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

    # Exibe o mapa
    st.plotly_chart(fig, use_container_width=True, config={"scrollZoom": True})

else:
    st.info("Por favor, envie um arquivo CSV para visualizar o mapa.")
