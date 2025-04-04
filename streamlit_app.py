    # Exibir dados com coordenadas ausentes ou suspeitas
    st.subheader("Corrigir coordenadas (latitude/longitude)")

    # Filtrar dados com lat/lon ausentes ou inválidas (fora dos limites do RS, por exemplo)
    df_para_editar = df[
        df['latitude'].isna() | df['longitude'].isna() |
        (df['latitude'] < -34) | (df['latitude'] > -27) |
        (df['longitude'] < -58) | (df['longitude'] > -48)
    ].copy()

    if not df_para_editar.empty:
        df_corrigido = st.data_editor(
            df_para_editar[['endereco', 'Municipio', 'latitude', 'longitude']],
            num_rows="dynamic",
            use_container_width=True,
            key="editor_corrigir_coords"
        )

        # Atualizar o DataFrame original com os dados corrigidos
        for idx in df_corrigido.index:
            df.loc[df_corrigido.index, 'latitude'] = df_corrigido['latitude']
            df.loc[df_corrigido.index, 'longitude'] = df_corrigido['longitude']
    else:
        st.info("Nenhum registro com coordenadas ausentes ou suspeitas.")
