import pandas as pd
import streamlit as st
import pydeck as pdk

# Configuração da página
st.set_page_config(page_title="Geodengue - Pydeck", layout="wide")

col1, col2, col3 = st.columns([1, 4, 1])
col1.image('https://github.com/andrejarenkow/csv/blob/master/logo_cevs%20(2).png?raw=true', width=100)
col2.header('Coordenadas Notificações Dengue')
col3.image('https://github.com/andrejarenkow/csv/blob/master/logo_estado%20(3)%20(1).png?raw=true', width=150)

st.sidebar.header("Upload do Arquivo")
uploaded_file = st.sidebar.file_uploader("Envie um arquivo CSV", type=["csv"])

if uploaded_file is not None:
    df_original = pd.read_csv(uploaded_file)

    df_original['CLASSI_FIN'] = df_original['CLASSI_FIN'].fillna('Em investigação').astype(str)
    df_original["DT_SIN_PRI"] = pd.to_datetime(df_original["DT_SIN_PRI"], errors="coerce")
    df_original = df_original[df_original['DT_SIN_PRI'].dt.year == 2025]
    df_original["Semana_Epidemiologica"] = df_original["DT_SIN_PRI"].dt.strftime('%Y-%U')
    df_original = df_original.sort_values(by="DT_SIN_PRI")

    dicionario_classifi = {
        '5.0': 'Descartado',
        '10.0': 'Dengue',
        '11.0': 'Dengue com sinais de alarme',
        '12.0': 'Dengue grave',
        '13.0': 'Chikungunya',
        '8.0': 'Fechado pelo sistema'
    }

    df_original['CLASSI_FIN'] = df_original['CLASSI_FIN'].replace(dicionario_classifi)

    # Filtro de município
    municipio = st.sidebar.selectbox("Selecione um município:", sorted(df_original['Municipio'].dropna().unique()))
    aplicar_filtro = st.sidebar.button("Aplicar Filtro")

    if aplicar_filtro:
        df = df_original[df_original['Municipio'] == municipio].copy()
    else:
        df = df_original.copy()

    st.subheader("Editar coordenadas diretamente na tabela")
    editable_cols = ["latitude", "longitude", "Municipio", "endereco", "CLASSI_FIN", "DT_SIN_PRI"]
    df_editado = st.data_editor(df[editable_cols], num_rows="dynamic", use_container_width=True)

    df.update(df_editado)

    # Filtra apenas pontos com coordenadas válidas
    df_valid = df.dropna(subset=["latitude", "longitude"])

    # Calcula centro do mapa
    if len(df_valid) > 0:
        lat_center = df_valid["latitude"].mean()
        lon_center = df_valid["longitude"].mean()
    else:
        lat_center, lon_center = -30.0, -51.0  # fallback

    st.subheader("Mapa Interativo com Pydeck")

    # Define cores por classificação
    color_map = {
        "Descartado": [128, 128, 128],
        "Dengue": [255, 165, 0],
        "Dengue com sinais de alarme": [255, 0, 0],
        "Dengue grave": [0, 0, 0],
        "Chikungunya": [0, 0, 255],
        "Fechado pelo sistema": [0, 128, 0],
        "Em investigação": [128, 0, 128],
    }

    df_valid["color"] = df_valid["CLASSI_FIN"].map(color_map)

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=df_valid,
        get_position='[longitude, latitude]',
        get_fill_color="color",
        get_radius=150,
        pickable=True,
        auto_highlight=True
    )

    tooltip = {
        "html": "<b>Município:</b> {Municipio}<br/>"
                "<b>Endereço:</b> {endereco}<br/>"
                "<b>Classificação:</b> {CLASSI_FIN}<br/>"
                "<b>Data:</b> {DT_SIN_PRI}",
        "style": {"backgroundColor": "steelblue", "color": "white"}
    }

    view_state = pdk.ViewState(latitude=lat_center, longitude=lon_center, zoom=10, pitch=0)

    r = pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip=tooltip, map_style='mapbox://styles/mapbox/light-v9')

    st.pydeck_chart(r)

    # Resumo dos dados faltantes
    st.markdown("### Resumo de dados faltantes por município")
    nan_por_municipio = df[df['latitude'].isna()].groupby('Municipio').size().reset_index(name='NaN_Latitude')
    total_por_municipio = df.groupby('Municipio').size().reset_index(name='Total_Registros')
    resultado = pd.merge(nan_por_municipio, total_por_municipio, on='Municipio', how='right').fillna(0)
    resultado['% NaN'] = round((resultado['NaN_Latitude'] / resultado['Total_Registros']) * 100)

    linha_total = pd.DataFrame({
        'Municipio': ['TOTAL'],
        'NaN_Latitude': [resultado['NaN_Latitude'].sum()],
        'Total_Registros': [resultado['Total_Registros'].sum()],
        '% NaN': [round((resultado['NaN_Latitude'].sum() / resultado['Total_Registros'].sum()) * 100, 2)]
    })

    resultado = pd.concat([resultado, linha_total], ignore_index=True)
    resultado.columns = ['Município', 'Não achados', 'Total notificações', 'Porcentagem']
    st.dataframe(resultado, hide_index=True)
