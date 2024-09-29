import oracledb
import os
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import matplotlib.pyplot as plt
import numpy as np
st.set_page_config(
    page_title="Monitoramento de Clima by DataStormTracker",
    page_icon="https://i.imgur.com/xxCZ8Ng.png",
    initial_sidebar_state="collapsed",
)

icon_html = """
<div style="position: fixed; bottom: 20px; right: 20px; z-index: 1000;">
    <a href="https://i.imgur.com/xxCZ8Ng.png" target="_blank">
        <img src="https://i.imgur.com/xxCZ8Ng.png" alt="Ícone" style="width: 70px; height: 70px;"/>
    </a>
</div>
"""

# Adicionando o ícone ao Streamlit
st.markdown(icon_html, unsafe_allow_html=True)
# Definir o caminho da pasta onde está a wallet
wallet_directory = r"C:\\Wallet_ORACLEDB"
os.environ['TNS_ADMIN'] = wallet_directory

# Inicializar o cliente Oracle com o caminho do Instant Client
oracledb.init_oracle_client(lib_dir=r"C:\\oracle\\instantclient_23_5")


# Função para obter dados do OracleDB
@st.cache_data
def get_data_from_oracle(query):
    try:
        with oracledb.connect(user="admin", password="Abacate1#Espacial1#", dsn="oracledb_high") as connection:
            df = pd.read_sql(query, connection)
        return df
    except Exception as e:
        st.error(f"Erro ao obter dados: {e}")
        return pd.DataFrame()


# Consulta SQL para clima atual de todos os postos
query_clima_postos = """
    SELECT 
        p.COD_POSTO, 
        p.NM_CIDADE_POSTO, 
        p.NR_LATI_CIDADE, 
        p.NR_LONGI_CIDADE, 
        c.NR_TEMP, 
        c.QTD_CHUVA, 
        c.NR_VEL_VT, 
        c.NR_DIR_VT, 
        c.data_hora
    FROM 
        T_DS_POSTO p
    JOIN 
        (SELECT * FROM T_DS_CLIMA_ATUAL WHERE id_clima IN (SELECT MAX(id_clima) FROM T_DS_CLIMA_ATUAL GROUP BY cod_posto)) c
    ON 
        p.COD_POSTO = c.COD_POSTO
"""

# Consulta SQL para alagamentos
query_alagamento = """
SELECT 
    a.COD_POSTO, 
    d.NM_CIDADE_POSTO,  
    a.ds_local,
    d.nr_lati_cidade,
    d.nr_longi_cidade,
    COALESCE(ROUND(AVG(b.QTD_CHUVA), 2), 2.5) AS MEDIA_CHUVA,
    (SELECT c.qtd_chuva
     FROM T_DS_CLIMA_ATUAL c
     WHERE c.cod_posto = a.cod_posto
     ORDER BY c.id_clima DESC
     FETCH FIRST 1 ROWS ONLY) AS QTD_CHUVA_ATUAL
FROM 
    T_DS_HIST_ALAGAMENTO a
JOIN 
    T_DS_BOLETIM_PLUVIO b ON a.COD_POSTO = b.COD_POSTO
JOIN
    T_DS_POSTO d ON a.COD_POSTO = d.COD_POSTO  
WHERE 
    b.DATA_HORA BETWEEN a.DATA_INICIO AND a.DATA_TERMINO
    AND b.QTD_CHUVA > 0
GROUP BY 
    a.COD_POSTO, d.NM_CIDADE_POSTO, a.ds_local, d.nr_lati_cidade, d.nr_longi_cidade
"""

# Consulta SQL para interrupções de energia
query_energia = """
SELECT 
    a.COD_POSTO, 
    d.NM_CIDADE_POSTO,  
    a.ds_causa,
    d.nr_lati_cidade AS NR_LATI_CIDADE,
    d.nr_longi_cidade AS NR_LONGI_CIDADE,
    ROUND(max(b.QTD_CHUVA), 2) AS MEDIA_CHUVA,
    (SELECT c.qtd_chuva
     FROM T_DS_CLIMA_ATUAL c
     WHERE c.cod_posto = a.cod_posto
     ORDER BY c.id_clima DESC
     FETCH FIRST 1 ROWS ONLY) AS QTD_CHUVA_ATUAL
FROM 
    T_DS_INTERUP_LUZ a
JOIN 
    T_DS_BOLETIM_PLUVIO b ON a.COD_POSTO = b.COD_POSTO
JOIN
    T_DS_POSTO d ON a.COD_POSTO = d.COD_POSTO  
WHERE 
    b.DATA_HORA BETWEEN a.DATA_INICIO AND a.DATA_TERMINO
    AND b.QTD_CHUVA > 0
GROUP BY 
    a.COD_POSTO, d.NM_CIDADE_POSTO, a.ds_causa, d.nr_lati_cidade, d.nr_longi_cidade
"""

#----------------------------------------Graficos-----------------------------------------------#
ocorrencias_luz_query = """
SELECT cod_posto, COUNT(*) AS num_ocorrencias
FROM t_ds_interup_luz
WHERE data_inicio BETWEEN TO_DATE('2020-01-01', 'YYYY-MM-DD') AND TO_DATE('2024-12-31', 'YYYY-MM-DD')
GROUP BY cod_posto
ORDER BY num_ocorrencias DESC
"""

alagamentos_query = """
SELECT cod_posto, ds_local, COUNT(*) AS num_alagamentos
FROM t_ds_hist_alagamento
WHERE data_inicio BETWEEN TO_DATE('2020-01-01', 'YYYY-MM-DD') AND TO_DATE('2024-12-31', 'YYYY-MM-DD')
GROUP BY cod_posto, ds_local
ORDER BY num_alagamentos DESC
"""

causas_interrupcao_query = """
SELECT ds_causa, COUNT(*) AS num_ocorrencias
FROM t_ds_interup_luz
WHERE ds_causa NOT IN ('NAO IDENTIFICADO')
GROUP BY ds_causa
HAVING COUNT(*) >= 2000
"""

precipitacao_query = """
SELECT cod_posto, SUM(qtd_chuva) AS precipitacao_total, data_hora
FROM t_ds_boletim_pluvio
WHERE data_hora BETWEEN TO_DATE('2020-01-01', 'YYYY-MM-DD') AND TO_DATE('2024-12-31', 'YYYY-MM-DD')
GROUP BY cod_posto, data_hora
ORDER BY data_hora
"""

Resumo_estatistico_query = """
    SELECT 
    p.COD_POSTO, 
    p.NM_CIDADE_POSTO,
    AVG(c.NR_TEMP) AS media_temp,
    MEDIAN(c.NR_TEMP) AS mediana_temp,
    STDDEV(c.NR_TEMP) AS desvio_temp,
    AVG(c.QTD_CHUVA) AS media_chuva,
    MEDIAN(c.QTD_CHUVA) AS mediana_chuva,
    STDDEV(c.QTD_CHUVA) AS desvio_chuva,
    AVG(c.NR_UMID) AS media_umidade,
    MEDIAN(c.NR_UMID) AS mediana_umidade,
    STDDEV(c.NR_UMID) AS desvio_umidade
FROM 
    T_DS_POSTO p
JOIN 
    T_DS_CLIMA_ATUAL c ON p.COD_POSTO = c.COD_POSTO
GROUP BY 
    p.COD_POSTO, p.NM_CIDADE_POSTO
"""
#----------------------------------------Graficos-----------------------------------------------#
# Carregar os dados
df_clima_postos = get_data_from_oracle(query_clima_postos)
df_alagamento = get_data_from_oracle(query_alagamento)
df_energia = get_data_from_oracle(query_energia)
df_energia['COD_POSTO'] = df_energia['COD_POSTO'].astype(str).str.replace(',', '')
df_alagamento['COD_POSTO'] = df_alagamento['COD_POSTO'].astype(str).str.replace(',', '')
df_clima_postos['COD_POSTO'] = df_clima_postos['COD_POSTO'].astype(str).str.replace(',', '')
df_energia = df_energia.groupby(['COD_POSTO', 'NM_CIDADE_POSTO', 'NR_LATI_CIDADE', 'NR_LONGI_CIDADE']).agg(
    QTD_CHUVA_ATUAL=('QTD_CHUVA_ATUAL', 'max'),
    MEDIA_CHUVA=('MEDIA_CHUVA', 'mean')
).reset_index()
# Verifica se a coluna 'data_hora' está presente em clima
if 'DATA_HORA' in df_clima_postos.columns:
    df_clima_postos['data_hora_formatada'] = pd.to_datetime(df_clima_postos['DATA_HORA']).dt.strftime('%d-%m-%Y %H:%M')

# Ajustar a MEDIA_CHUVA em alagamento
df_alagamento['MEDIA_CHUVA'] = df_alagamento['MEDIA_CHUVA'].apply(lambda x: max(x, 4.5))

# Ajustar a MEDIA_CHUVA em energia
df_energia['MEDIA_CHUVA'] = df_energia['MEDIA_CHUVA'].apply(lambda x: max(x, 7.5))


# Calcular probabilidade de alagamento
def calcular_probabilidade_alagamento(row):
    qtd_chuva_atual = row['QTD_CHUVA_ATUAL']
    media_chuva = row['MEDIA_CHUVA']

    # Lógica para calcular a probabilidade de alagamento
    # Por exemplo, mapeando a quantidade de chuva atual para a probabilidade
    if qtd_chuva_atual >= 4.5 * media_chuva:
        probabilidade = 90
    elif qtd_chuva_atual >= 3.5 * media_chuva:
        probabilidade = (qtd_chuva_atual - (3.0 * media_chuva)) / (4.0 * media_chuva - (3.0 * media_chuva)) * (90 - 80) + 80
    elif qtd_chuva_atual >= 2.5 * media_chuva:
        probabilidade = (qtd_chuva_atual - (2.0 * media_chuva)) / (3.0 * media_chuva - (2.0 * media_chuva)) * (80 - 70) + 70
    elif qtd_chuva_atual >= media_chuva:
        probabilidade = (qtd_chuva_atual - media_chuva) / (2.0 * media_chuva - media_chuva) * (70 - 60) + 60
    else:
        probabilidade = 0

    # Limitar a probabilidade máxima a 90
    probabilidade = min(probabilidade, 90)

    return round(probabilidade, 2)



# Calcular probabilidade de queda de energia
def calcular_probabilidade_queda_energia(row):
    qtd_chuva_atual = row['QTD_CHUVA_ATUAL']
    media_chuva = row['MEDIA_CHUVA']

    # Lógica para calcular a probabilidade de queda de energia
    if qtd_chuva_atual >= 3.5 * media_chuva:
        probabilidade = 90
    elif qtd_chuva_atual >= 2.5 * media_chuva:
        probabilidade = (qtd_chuva_atual - (3.0 * media_chuva)) / (4.0 * media_chuva - (3.0 * media_chuva)) * (90 - 80) + 80
    elif qtd_chuva_atual >= 1.5 * media_chuva:
        probabilidade = (qtd_chuva_atual - (2.0 * media_chuva)) / (3.0 * media_chuva - (2.0 * media_chuva)) * (80 - 70) + 70
    elif qtd_chuva_atual >= media_chuva:
        probabilidade = (qtd_chuva_atual - media_chuva) / (2.0 * media_chuva - media_chuva) * (70 - 60) + 60
    else:
        probabilidade = 0

    return round(probabilidade, 2)

for _, row in df_clima_postos.iterrows():
    data_hora = row['data_hora_formatada'] if 'data_hora_formatada' in df_clima_postos.columns else "N/A"
# Adicionar probabilidade às tabelas
df_alagamento['PROB_ALAGAMENTO'] = df_alagamento.apply(calcular_probabilidade_alagamento, axis=1)
df_energia['PROB_QUEDA_ENERGIA'] = df_energia.apply(calcular_probabilidade_queda_energia, axis=1)
df_alagamento = df_alagamento[df_alagamento['PROB_ALAGAMENTO'] >= 60]
df_energia = df_energia[df_energia['PROB_QUEDA_ENERGIA'] >= 60]
ocorrencias_luz = get_data_from_oracle(ocorrencias_luz_query)
alagamentos = get_data_from_oracle(alagamentos_query)
causas_interrupcao = get_data_from_oracle(causas_interrupcao_query)
precipitacao = get_data_from_oracle(precipitacao_query)
Resumo_estatistico = get_data_from_oracle(Resumo_estatistico_query )
st.sidebar.title("Menu")
sidebar_option = st.sidebar.radio("Selecione uma aba:", ("Mapas", "Gráficos"))
if sidebar_option == "Gráficos":
    grafico_selecionado = st.selectbox("Escolha o gráfico a ser exibido:",
                                       ["Maiores Ocorrências de Falhas Energeticas por Posto",
                                        "Ocorrências de Alagamentos por Rua",
                                        "Distribuição de Causas: Falhas Energeticas",
                                        "Resumo Estatístico",
                                        "Precipitação Acumulada ao Longo do Tempo"])
    df_clima_postos = get_data_from_oracle(query_clima_postos)
    mapeamento_postos = dict(zip(df_clima_postos['COD_POSTO'], df_clima_postos['NM_CIDADE_POSTO']))


    if grafico_selecionado == "Maiores Ocorrências de Falhas Energeticas por Posto":
        st.markdown("<h2 style='text-align: center;'>Maiores Ocorrências de Falhas Energeticas por Posto</h2>", unsafe_allow_html=True)

        if 'COD_POSTO' in ocorrencias_luz.columns and 'NUM_OCORRENCIAS' in ocorrencias_luz.columns:
            total_ocorrencias = sum(ocorrencias_luz['NUM_OCORRENCIAS'])
            ocorrencias_luz['PERCENTUAL'] = (ocorrencias_luz['NUM_OCORRENCIAS'] / total_ocorrencias) * 100
            ocorrencias_luz_filtrado = ocorrencias_luz[ocorrencias_luz['PERCENTUAL'] > 3]

            if not ocorrencias_luz_filtrado.empty:
                total_ocorrencias_filtradas = sum(ocorrencias_luz_filtrado['NUM_OCORRENCIAS'])
                fig, ax = plt.subplots(figsize=(10, 7), facecolor='none')
                cores = plt.cm.tab20.colors
                num_postos = len(ocorrencias_luz_filtrado)
                cores = cores[:num_postos]
                ocorrencias_luz_filtrado['NM_CIDADE_POSTO'] = ocorrencias_luz_filtrado['COD_POSTO'].map(
                    mapeamento_postos)
                wedges, texts, autotexts = ax.pie(
                    ocorrencias_luz_filtrado['NUM_OCORRENCIAS'],
                    autopct='%1.1f%%',  # Mostrar as porcentagens
                    startangle=90,
                    textprops=dict(color="w"),
                    colors=cores,
                    pctdistance=1.08
                )
                ocorrencias_luz_sorted = ocorrencias_luz_filtrado.sort_values(by='NUM_OCORRENCIAS', ascending=False)
                legend_data = [
                    (posto, count, count / total_ocorrencias_filtradas * 100)

                    for posto, count in
                    zip(ocorrencias_luz_sorted['NM_CIDADE_POSTO'], ocorrencias_luz_sorted['NUM_OCORRENCIAS'])
                ]
                ax.legend(
                    wedges,
                    [f'{posto}: {count} ({percent:.1f}%)' for posto, count, percent in legend_data],
                    title="Principais postos (Falta de Luz)",
                    loc="center left",
                    bbox_to_anchor=(0.13, -0.29),
                    ncol=2
                )
                ax.axis('equal')
                st.pyplot(fig, bbox_inches='tight', transparent=True)
            else:
                st.write("Nenhum posto com mais de 3% de ocorrências de falta de luz.")
        else:
            st.error("Erro: Colunas 'COD_POSTO' e/ou 'NUM_OCORRENCIAS' não estão presentes no DataFrame.")



    elif grafico_selecionado == "Ocorrências de Alagamentos por Rua":
        st.markdown("<h2 style='text-align: center;'>Ocorrências de Alagamentos por Rua </h2>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center;'>(2020-2024)</h2>",
                    unsafe_allow_html=True)
        alagamentos_filtrados = alagamentos[alagamentos['NUM_ALAGAMENTOS'] > 10]

        if not alagamentos_filtrados.empty:
            fig, ax = plt.subplots(figsize=(20, 10), facecolor='w')  # Fundo branco externo
            unique_postos = alagamentos_filtrados['COD_POSTO'].unique()
            colors = plt.cm.tab20(np.linspace(0, 1, len(unique_postos)))
            color_map = {posto: color for posto, color in zip(unique_postos, colors)}
            bar_colors = [color_map[posto] for posto in alagamentos_filtrados['COD_POSTO']]
            bars = ax.bar(alagamentos_filtrados['DS_LOCAL'], alagamentos_filtrados['NUM_ALAGAMENTOS'], color=bar_colors)

            for bar in bars:
                yval = bar.get_height()
                ax.text(bar.get_x() + bar.get_width() / 2, yval + 1, int(yval), va='bottom', ha='center', color='white',
                        fontsize=15)
            # Configurar o gráfico
            ax.spines['bottom'].set_color('white')
            ax.spines['left'].set_color('white')
            ax.spines['right'].set_color('white')
            ax.spines['top'].set_color('white')
            ax.xaxis.label.set_color('white')
            ax.yaxis.label.set_color('white')
            ax.tick_params(axis='x', colors='white')
            ax.tick_params(axis='y', colors='white')
            ax.set_xlabel("Rua")
            ax.set_ylabel("Número de Alagamentos")
            ax.set_xticks([])

            legend_labels = [f'{rua} (cod: {cod}): {num}'

                             for rua, cod, num in
                             zip(alagamentos_filtrados['DS_LOCAL'], alagamentos_filtrados['COD_POSTO'],
                                 alagamentos_filtrados['NUM_ALAGAMENTOS'])]
            ax.legend(bars,
                      legend_labels,
                      title="Ruas (Cod do Posto):Numero de Ocorencias",
                      title_fontsize=25,
                      loc='upper center',
                      bbox_to_anchor=(0.5, -0.15),  # Posiciona a legenda abaixo do gráfico
                      fontsize=16,
                      ncol=2)  # Legenda com 4 colunas
            st.pyplot(fig, bbox_inches='tight', transparent=True)



    elif grafico_selecionado == "Distribuição de Causas: Falhas Energeticas":
        st.markdown("<h2 style='text-align: center;'>Distribuição de Causas: Falhas Energeticas</h2>",unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center;'>\n</h2>",unsafe_allow_html=True)
        fig, ax = plt.subplots(figsize=(10, 7), facecolor='none')
        causas_interrupcao = causas_interrupcao.sort_values(by='NUM_OCORRENCIAS', ascending=False)
        wedges, texts, autotexts = plt.pie(causas_interrupcao['NUM_OCORRENCIAS'],
                                           labels=None,
                                           autopct='%1.1f%%',
                                           startangle=90,
                                           textprops=dict(color="w"),
                                           pctdistance = 1.15)

        for autotext in autotexts:
            autotext.set_fontsize(12)
        plt.legend(wedges,
                   [f'{label}: {count} ({count / sum(causas_interrupcao["NUM_OCORRENCIAS"]) * 100:.1f}%)'
                    for label, count in zip(causas_interrupcao['DS_CAUSA'], causas_interrupcao['NUM_OCORRENCIAS'])],
                   title="Causas de Interrupções",
                   loc="center left",
                   ncol=2,
                   bbox_to_anchor=(-0.20, -0.11))
        st.pyplot(fig, bbox_inches='tight', transparent=True)



    elif grafico_selecionado == "Precipitação Acumulada ao Longo do Tempo":
        st.markdown("<h2 style='text-align: center;'>Precipitação Acumulada ao Longo do Tempo </h2>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center;'>(2020-2024)</h2>", unsafe_allow_html=True)
        precipitacao_acumulada = precipitacao.groupby('DATA_HORA')['PRECIPITACAO_TOTAL'].sum().cumsum()

        if not precipitacao_acumulada.empty:
            fig, ax = plt.subplots(figsize=(10, 5), facecolor='none')  # Fundo da figura transparente
            ax.fill_between(precipitacao_acumulada.index, precipitacao_acumulada, color="skyblue", alpha=0.4)
            ax.set_facecolor('none')
            ax.set_xlabel("Ano", color='white')
            ax.set_ylabel("Precipitação Acumulada (mm)", color='white')
            ax.spines['bottom'].set_color('white')
            ax.spines['left'].set_color('white')
            ax.spines['right'].set_color('white')
            ax.spines['top'].set_color('white')
            ax.tick_params(axis='x', colors='white')  # Eixo X branco
            ax.tick_params(axis='y', colors='white')  # Eixo Y branco
            st.pyplot(fig)

        else:
            st.write("Nenhum dado disponível para exibir o gráfico.")


    elif grafico_selecionado == "Resumo Estatístico":
        st.markdown("<h2 style='text-align: center;'>Resumo Estatístico do Clima Atual</h2>", unsafe_allow_html=True)

        # Exibir as estatísticas de clima
        if not Resumo_estatistico.empty:
            # Selecionar apenas as colunas relevantes para visualização
            colunas_relevantes = [
                'COD_POSTO',
                'NM_CIDADE_POSTO',
                'MEDIA_TEMP',
                'MEDIANA_TEMP',
                'DESVIO_TEMP',
                'MEDIA_CHUVA',
                'MEDIANA_CHUVA',
                'DESVIO_CHUVA',
                'MEDIA_UMIDADE',
                'MEDIANA_UMIDADE',
                'DESVIO_UMIDADE'
            ]

            # Verificar se as colunas estão no DataFrame
            colunas_presentes = [col for col in colunas_relevantes if col in Resumo_estatistico.columns]

            # Arredondar os valores para duas casas decimais
            Resumo_estatistico[colunas_presentes] = Resumo_estatistico[colunas_presentes].round(2)


            st.dataframe(Resumo_estatistico[colunas_presentes].style.format({
                'MEDIA_TEMP': '{:.2f}',
                'MEDIANA_TEMP': '{:.2f}',
                'DESVIO_TEMP': '{:.2f}',
                'MEDIA_CHUVA': '{:.2f}',
                'MEDIANA_CHUVA': '{:.2f}',
                'DESVIO_CHUVA': '{:.2f}',
                'MEDIA_UMIDADE': '{:.2f}',
                'MEDIANA_UMIDADE': '{:.2f}',
                'DESVIO_UMIDADE': '{:.2f}',
            }))
        else:
            st.write("Nenhum dado disponível para o resumo estatístico do clima atual.")
if sidebar_option == "Mapas":
    option = st.selectbox("Selecione o tipo de visualização:", ("Todos os Postos", "Alagamentos", "Quedas de Energia"))

    # Tabela e mapa para Todos os Postos
    if option == "Todos os Postos":
        st.title("Monitoramento de Clima")
        st.write("Visualização de todos os postos com clima atual")

        # Mapa
        mapa = folium.Map(location=[-23.63706573331013, -46.63976976262687], zoom_start=9.5)

        # Tabela
        tabela_postos = []

        for _, row in df_clima_postos.iterrows():
            cod_posto = row['COD_POSTO']
            nome_posto = row['NM_CIDADE_POSTO']
            latitude = row['NR_LATI_CIDADE']
            longitude = row['NR_LONGI_CIDADE']
            chuva = row['QTD_CHUVA'] if pd.notna(row['QTD_CHUVA']) else "N/A"
            temp = row['NR_TEMP'] if pd.notna(row['NR_TEMP']) else "N/A"
            vel_vt = row['NR_VEL_VT'] if pd.notna(row['NR_VEL_VT']) else "N/A"
            dir_vt = row['NR_DIR_VT'] if pd.notna(row['NR_DIR_VT']) else "N/A"
            data_hora = row['data_hora_formatada'] if 'data_hora_formatada' in df_clima_postos.columns else "N/A"
            # Adicionar à tabela
            tabela_postos.append({
                'Posto': nome_posto,
                'Código': cod_posto,
                'Temperatura': f"{temp} °C",
                'Chuva': f"{chuva} mm",
                'Velocidade Vento': f"{vel_vt} m/s",
                'Direção Vento': f"{dir_vt} °"
            })

            # Adicionar marcador ao mapa
            descricao = f"""
                <b>Posto:</b> {nome_posto} ({cod_posto})<br>
                <b>Temperatura:</b> {temp} °C<br>
                <b>Chuva:</b> {chuva} mm<br>
                <b>Velocidade do Vento:</b> {vel_vt} m/s<br>
                <b>Direção do Vento:</b> {dir_vt} °<br>
                <b>Última atualização:</b> {data_hora}
            """
            folium.Marker(
                location=[latitude, longitude],
                popup=folium.Popup(descricao, max_width=300),
                icon=folium.Icon(color='blue')
            ).add_to(mapa)

        # Exibir mapa
        st_folium(mapa, width=725,height=400)

        # Exibir tabela
        if tabela_postos:
            df_tabela_postos = pd.DataFrame(tabela_postos)
            st.subheader("Tabela de Postos")
            st.dataframe(df_tabela_postos, use_container_width=True)
        else:
            st.write("Nenhum posto encontrado.")

    # Tabela e mapa para Alagamentos
    elif option == "Alagamentos":
        st.title("Monitoramento de Alagamentos")
        st.write("Visualização de postos com possível alagamento")

        # Mapa de alagamentos
        mapa_alagamento = folium.Map(location=[-23.63706573331013, -46.63976976262687], zoom_start=9.5)

        # Tabela
        tabela_alagamento = []

        for _, row in df_alagamento.iterrows():
            cod_posto = row['COD_POSTO']
            nome_posto = row['NM_CIDADE_POSTO']
            Local = row['DS_LOCAL']
            latitude = row['NR_LATI_CIDADE']
            longitude = row['NR_LONGI_CIDADE']
            media_chuva = row['MEDIA_CHUVA']
            chuva_atual = row['QTD_CHUVA_ATUAL']
            probabilidade = row['PROB_ALAGAMENTO']

            # Adicionar à tabela
            tabela_alagamento.append({
                'Código': cod_posto,
                'Posto': nome_posto,
                'Local': Local,
                'Média Chuva': f"{media_chuva} mm/s",
                'Chuva Atual': f"{chuva_atual} mm/s",
                'Prob. Alagamento': f"{probabilidade} %"
            })

            # Adicionar marcador ao mapa
            descricao = f"""
                <b>Posto:</b> {nome_posto} ({cod_posto})<br>
                <b>Média de Chuva:</b> {media_chuva} mm/s<br>
                <b>Chuva Atual:</b> {chuva_atual} mm/s<br>
                <b>Última atualização:</b> {data_hora}
            """
            folium.Marker(
                location=[latitude, longitude],
                popup=folium.Popup(descricao, max_width=300),
                icon=folium.CustomIcon('https://i.imgur.com/cNLYC9g.png', icon_size=(50, 45))
            ).add_to(mapa_alagamento)
        # Exibir mapa
        st_folium(mapa_alagamento, width=725,height=400)

        # Exibir tabela
        if tabela_alagamento:
            df_tabela_alagamento = pd.DataFrame(tabela_alagamento)
            postos_disponiveis = df_tabela_alagamento['Código'].unique()
            selected_posto = st.selectbox("Selecione um Posto:", postos_disponiveis)
            filtered_tabela_data = df_tabela_alagamento[df_tabela_alagamento['Código'] == selected_posto]
            st.subheader("Tabela de Alagamentos")
            st.dataframe(filtered_tabela_data, use_container_width=True)
        else:
            st.write("Nenhum posto com possível alagamento encontrado.")

    # Tabela e mapa para Quedas de Energia
    elif option == "Quedas de Energia":
        st.title("Monitoramento de Falhas Energeticas")
        st.write("Visualização de postos com possível queda de energia")

        # Mapa de quedas de energia
        mapa_energia = folium.Map(location=[-23.63706573331013, -46.63976976262687], zoom_start=9.5)

        # Tabela
        tabela_energia = []

        for _, row in df_energia.iterrows():
            cod_posto = row['COD_POSTO']
            nome_posto = row['NM_CIDADE_POSTO']
            latitude = row['NR_LATI_CIDADE']
            longitude = row['NR_LONGI_CIDADE']
            media_chuva = round(row['MEDIA_CHUVA'],2)
            chuva_atual = row['QTD_CHUVA_ATUAL']
            probabilidade = row['PROB_QUEDA_ENERGIA']

            # Adicionar à tabela
            tabela_energia.append({
                'Posto': nome_posto,
                'Código': cod_posto,
                'Média Chuva': f"{media_chuva} mm",
                'Chuva Atual': f"{chuva_atual} mm",
                'Prob. Queda de Energia': f"{probabilidade} %"
            })

            # Adicionar marcador ao mapa
            descricao = f"""
                <b>Posto:</b> {nome_posto} ({cod_posto})<br>
                <b>Média de Chuva:</b> {media_chuva} mm<br>
                <b>Chuva Atual:</b> {chuva_atual} mm<br>
                <b>Probabilidade de Queda de Energia:</b> {probabilidade} %
                <b>Última atualização:</b> {data_hora}
            """
            folium.Marker(
                location=[latitude, longitude],
                popup=folium.Popup(descricao, max_width=300),
                icon=folium.CustomIcon('https://i.imgur.com/5V6SB0V.png', icon_size=(65, 45))
            ).add_to(mapa_energia)

        # Exibir mapa
        st_folium(mapa_energia, width=725,height=400)

        # Exibir tabela
        if tabela_energia:
            df_tabela_energia = pd.DataFrame(tabela_energia)
            st.subheader("Tabela de Quedas de Energia")
            st.dataframe(df_tabela_energia, use_container_width=True)
        else:
            st.write("Nenhum posto com possível queda de energia encontrado.")