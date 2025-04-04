import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff  # Import necessário para hexbin
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
    usar_hexbin = st.sidebar.checkbox("Exibir como hexbin")  # NOVO
    usar_animacao = st.sidebar.checkbox("Ativar animação cumulativa")

    lat_center = (df['latitude'].max() + df['latitude'].min()) / 2
    lon_center = (df['longitude'].max() + df['longitude'].min()) / 2
    zoom_ini = 5.5

    if aplicar_filtro:
        df = df[df['Municipio'] == municipio]
        lat_center = (df['latitude'].max() + df['latitude'].min()) / 2
        lon_center = (df['longitude'].max() + df['longitude'].min()) / 2
        zoom_ini = 10

    st.subheader("Corrigir coordenadas (latitude/longitude)")
    df_para_editar = df[
        df['latitude'].isna() | df['longitude'].isna() |
        (df['latitude'] < -34) | (df['latitude'] > -27) |
        (df['longitude'] < -58) | (df['longitude'] > -48)
    ].copy()

    if df_para_editar.empty:
        df_corrigido = st.data_editor(
            df_para_editar[['endereco', 'Municipio', 'latitude', 'longitude']],
            num_rows="dynamic",
            use_container_width=True,
            key="editor_corrigir_coords"
        )

        for idx in df_corrigido.index:
            df.loc[idx, 'latitude'] = df_corrigido.loc[idx, 'latitude']
            df.loc[idx, 'longitude'] = df_corrigido.loc[idx, 'longitude']
    #else:
        #st.info("Nenhum registro com coordenadas ausentes ou suspeitas.")

    if usar_animacao:
        semanas_unicas = sorted(df["Semana_Epidemiologica"].unique())
        df_cumulativo = pd.DataFrame()
        for semana in semanas_unicas:
            df_temp = df[df["Semana_Epidemiologica"] <= semana].copy()
            df_temp["Semana_Cumulativa"] = semana
            df_cumulativo = pd.concat([df_cumulativo, df_temp])
        df = df_cumulativo

    # Geração do mapa
    if mapa_calor:
        fig = px.density_mapbox(
            df,
            lat="latitude",
            lon="longitude",
            radius=10,
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
            nx_hexagon=50,
            opacity=0.7,
            labels={"color": "Número de notificações"},
            min_count=1,
            color_continuous_scale="Reds",
            show_original_data=True,
            original_data_marker=dict(size=4, opacity=0.4, color="black"),
            center={"lat": lat_center, "lon": lon_center},
            mapbox_style='open-street-map',
            zoom=zoom_ini,
            height=800,
            width=800,
            range_color = [1,10]
        )
    else:
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
            "opacity": 0.7,
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

    st.plotly_chart(fig, use_container_width=True, config={"scrollZoom": True})

    nan_por_municipio = df[df['latitude'].isna()].groupby('Municipio').size().reset_index(name='NaN_Latitude')
    total_por_municipio = df.groupby('Municipio').size().reset_index(name='Total_Registros')
    resultado = pd.merge(nan_por_municipio, total_por_municipio, on='Municipio', how='right').fillna(0)
    resultado['% NaN'] = round((resultado['NaN_Latitude'] / resultado['Total_Registros']) * 100)

    linha_total = pd.DataFrame({
        'Municipio': ['TOTAL'],
        'NaN_Latitude': [resultado['NaN_Latitude'].sum()],
        'Total_Registros': [resultado['Total_Registros'].sum()],
        '% NaN': [(resultado['NaN_Latitude'].sum() / resultado['Total_Registros'].sum()) * 100]
    })

    resultado = pd.concat([resultado, linha_total], ignore_index=True)
    resultado.columns = ['Município', 'Não achados', 'Total notificações', 'Porcentagem']
    st.dataframe(resultado, hide_index=True)
