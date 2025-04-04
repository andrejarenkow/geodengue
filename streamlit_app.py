import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff

# Simulando carregamento de dados (substitua pelo seu dataframe real)
# df = pd.read_csv("seuarquivo.csv") 
# Para exemplo:
df = px.data.carshare().rename(columns={"centroid_lat": "latitude", "centroid_lon": "longitude"})
df["endereco"] = "Exemplo de endereço"
df["CLASSI_FIN"] = ["Dengue", "Descartado", "Dengue com sinais de alarme", "Em investigação"] * (len(df) // 4)

# Centralização e zoom
lat_center = df["latitude"].mean()
lon_center = df["longitude"].mean()
zoom_ini = 8

# Sidebar
st.sidebar.title("Opções de visualização")
usar_heatmap = st.sidebar.checkbox("Usar mapa de calor")
usar_hexbin = st.sidebar.checkbox("Usar mapa hexbin")

# Força a exclusividade entre os dois checkboxes
if usar_heatmap and usar_hexbin:
    st.sidebar.warning("Escolha apenas um tipo de visualização: Heatmap ou Hexbin.")
    st.stop()

# Token Mapbox
try:
    mapbox_token = open(".mapbox_token").read()
    px.set_mapbox_access_token(mapbox_token)
except:
    st.warning("Token do Mapbox não encontrado. Coloque seu token no arquivo `.mapbox_token`.")
    mapbox_token = None

# Criação do mapa
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
            "Em investigação": "purple"
        }
    )

# Exibe o mapa
st.plotly_chart(fig, use_container_width=True, config={"scrollZoom": True})
