import requests
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Tokens
TOKEN_1 = "f00dd5e97d583b4341f95ef9b79212bb"
TOKEN_2 = "6bdf2d630763755f76b9914a6dfbb8d3"


# Função para consultar a previsão do tempo para os próximos 5 dias na cidade
def consulta_previsao_tempo(id_cidade, token):
    try:
        url = f"http://apiadvisor.climatempo.com.br/api/v1/forecast/locale/{id_cidade}/days/15?token={token}"
        response = requests.get(url)
        response.raise_for_status()
        retorno_req = response.json()
        return retorno_req
    except requests.exceptions.RequestException:
        if token == TOKEN_1:
            return consulta_previsao_tempo(id_cidade, TOKEN_2)
        else:
            st.error("Ocorreu um erro ao tentar obter a previsão do tempo. Por favor, tente novamente mais tarde.")
            return None


# Função para consultar o clima atual na cidade
def consulta_clima_atual(id_cidade, token):
    try:
        url = f"http://apiadvisor.climatempo.com.br/api/v1/weather/locale/{id_cidade}/current?token={token}"
        response = requests.get(url)
        response.raise_for_status()
        retorno_req = response.json()
        return retorno_req
    except requests.exceptions.RequestException:
        if token == TOKEN_1:
            return consulta_clima_atual(id_cidade, TOKEN_2)
        else:
            st.error("Ocorreu um erro ao tentar obter o clima atual. Por favor, tente novamente mais tarde.")
            return None


# Função para consultar a previsão do tempo para as próximas 5 horas
def consulta_previsao_proximas_5_horas(id_cidade, token):
    try:
        url = f"http://apiadvisor.climatempo.com.br/api/v1/forecast/locale/{id_cidade}/hours/5?token={token}"
        response = requests.get(url)
        response.raise_for_status()
        retorno_req = response.json()
        return retorno_req
    except requests.exceptions.RequestException:
        if token == TOKEN_1:
            return consulta_previsao_proximas_5_horas(id_cidade, TOKEN_2)
        else:
            st.error(
                "Ocorreu um erro ao tentar obter a previsão das próximas 5 horas. Por favor, tente novamente mais tarde.")
            return None


# Função para obter a lista de cidades no estado de SP
def obter_cidades_sp():
    try:
        url = f"http://apiadvisor.climatempo.com.br/api/v1/locale/city?state=SP&token={TOKEN_1}"
        response = requests.get(url)
        response.raise_for_status()
        cidades = response.json()
        return cidades
    except requests.exceptions.RequestException:
        return obter_cidades_sp_com_token(TOKEN_2)


def obter_cidades_sp_com_token(token):
    try:
        url = f"http://apiadvisor.climatempo.com.br/api/v1/locale/city?state=SP&token={token}"
        response = requests.get(url)
        response.raise_for_status()
        cidades = response.json()
        return cidades
    except requests.exceptions.RequestException:
        st.error("Ocorreu um erro ao tentar obter a lista de cidades. Por favor, tente novamente mais tarde.")
        return None


# Página principal
def main():
    st.title("Consulta de Previsão do Tempo")

    # Seleção da cidade
    cidades_sp = obter_cidades_sp()
    if cidades_sp is not None:
        cidades_nomes = [cidade['name'] for cidade in cidades_sp]

        # Adiciona uma opção vazia no início da lista de cidades
        cidade_selecionada = st.selectbox("Escolha a cidade para consulta:", [""] + cidades_nomes)

        if cidade_selecionada:
            id_cidade = next(cidade['id'] for cidade in cidades_sp if cidade['name'] == cidade_selecionada)

            consulta_tipo = st.radio("Escolha o tipo de consulta:",
                                     ("Clima Atual", "Previsão dos Próximos Dias", "Previsão das Próximas 5 Horas"))

            if st.button("Consultar"):
                if consulta_tipo == "Clima Atual":
                    clima_atual = consulta_clima_atual(id_cidade, TOKEN_1)
                    if clima_atual is None:
                        clima_atual = consulta_clima_atual(id_cidade, TOKEN_2)
                    if clima_atual is not None:
                        if 'detail' in clima_atual:
                            st.error("ID da cidade inválido. Por favor, insira um ID válido.")
                            return
                        st.subheader("Clima Atual")
                        st.write("Condição: ", clima_atual['data']['condition'])
                        st.write("Temperatura: ", clima_atual['data']['temperature'], "°C")
                        st.write("Umidade: ", clima_atual['data']['humidity'], "%")
                        st.write("Pressão: ", clima_atual['data']['pressure'], "hPa")

                elif consulta_tipo == "Previsão dos Próximos Dias":
                    previsao_tempo = consulta_previsao_tempo(id_cidade, TOKEN_1)
                    if previsao_tempo is None:
                        previsao_tempo = consulta_previsao_tempo(id_cidade, TOKEN_2)
                    if previsao_tempo is not None:
                        if 'detail' in previsao_tempo:
                            st.error("ID da cidade inválido. Por favor, insira um ID válido.")
                            return
                        st.subheader("Previsão do Tempo para os Próximos Dias")

                        data = []
                        for dia in previsao_tempo['data']:
                            data.append([
                                dia['date_br'].split(',')[0],
                                dia['temperature']['min'],
                                dia['temperature']['max'],
                                dia['rain']['probability'],
                                dia['text_icon']['text']['phrase']['reduced']
                            ])

                        df = pd.DataFrame(data, columns=['Data', 'Temperatura Mínima (°C)', 'Temperatura Máxima (°C)',
                                                         'Probabilidade de Chuva (%)', 'Resumo'])

                        st.write(df)

                        dias = [dia['date_br'].split(',')[0] for dia in previsao_tempo['data']]
                        chuva = [dia['rain']['probability'] for dia in previsao_tempo['data']]
                        temperatura_min = [dia['temperature']['min'] for dia in previsao_tempo['data']]
                        temperatura_max = [dia['temperature']['max'] for dia in previsao_tempo['data']]

                        fig, ax = plt.subplots(1, 2, figsize=(12, 6))

                        ax[0].plot(dias, chuva, marker='o')
                        ax[0].set_title('Probabilidade de Chuva (%)')
                        ax[0].set_xlabel('Data')
                        ax[0].set_ylabel('Probabilidade de Chuva (%)')
                        ax[0].grid(True)

                        ax[1].plot(dias, temperatura_min, label='Mínima', marker='o')
                        ax[1].plot(dias, temperatura_max, label='Máxima', marker='o')
                        ax[1].set_title('Temperatura (°C)')
                        ax[1].set_xlabel('Data')
                        ax[1].set_ylabel('Temperatura (°C)')
                        ax[1].legend()
                        ax[1].grid(True)

                        ax[0].set_xticklabels(dias, rotation=45)
                        ax[1].set_xticklabels(dias, rotation=45)
                        ax[0].set_xlabel('Data')
                        ax[1].set_xlabel('Data')

                        st.pyplot(fig)

                elif consulta_tipo == "Previsão das Próximas 5 Horas":
                    previsao_5_horas = consulta_previsao_proximas_5_horas(id_cidade, TOKEN_1)
                    if previsao_5_horas is None:
                        previsao_5_horas = consulta_previsao_proximas_5_horas(id_cidade, TOKEN_2)
                    if previsao_5_horas is not None:
                        if 'detail' in previsao_5_horas:
                            st.error("ID da cidade inválido. Por favor, insira um ID válido.")
                            return
                        st.subheader("Previsão das Próximas 5 Horas")

                        agora = datetime.now()
                        cinco_horas = [agora + timedelta(hours=i) for i in range(5)]
                        data = []
                        for registro in previsao_5_horas['data']:
                            timestamp = datetime.fromtimestamp(registro['timestamp'])
                            if timestamp in cinco_horas:
                                data.append([
                                    timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                                    registro['temperature'],
                                    registro['humidity'],
                                    registro['pressure'],
                                    registro['wind']['velocity'],
                                    registro['wind']['direction'],
                                    registro['rain']['precipitation']
                                ])

                        df = pd.DataFrame(data, columns=['Hora', 'Temperatura (°C)', 'Umidade (%)', 'Pressão (hPa)',
                                                         'Velocidade do Vento (km/h)', 'Direção do Vento (°)',
                                                         'Precipitação de Chuva (mm)'])

                        st.write(df)

                        horas = [registro['timestamp'] for registro in previsao_5_horas['data'] if datetime.fromtimestamp(registro['timestamp']) in cinco_horas]
                        temperaturas = [registro['temperature'] for registro in previsao_5_horas['data'] if datetime.fromtimestamp(registro['timestamp']) in cinco_horas]
                        umidades = [registro['humidity'] for registro in previsao_5_horas['data'] if datetime.fromtimestamp(registro['timestamp']) in cinco_horas]
                        precipitacoes = [registro['rain']['precipitation'] for registro in previsao_5_horas['data'] if datetime.fromtimestamp(registro['timestamp']) in cinco_horas]

                        fig, ax1 = plt.subplots(figsize=(12, 6))

                        ax1.set_xlabel('Hora')
                        ax1.set_ylabel('Temperatura (°C)', color='tab:blue')
                        ax1.plot(horas, temperaturas, color='tab:blue', marker='o', label='Temperatura')
                        ax1.tick_params(axis='y', labelcolor='tab:blue')
                        ax1.set_xticks(horas)
                        ax1.set_xticklabels([datetime.fromtimestamp(h).strftime("%H:%M") for h in horas], rotation=45)

                        ax2 = ax1.twinx()
                        ax2.set_ylabel('Precipitação de Chuva (mm)', color='tab:green')
                        ax2.plot(horas, precipitacoes, color='tab:green', marker='o', label='Precipitação')
                        ax2.tick_params(axis='y', labelcolor='tab:green')

                        fig.tight_layout()
                        st.pyplot(fig)

if __name__ == "__main__":
    main()
