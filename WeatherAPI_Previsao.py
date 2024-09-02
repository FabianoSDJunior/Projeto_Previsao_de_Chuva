import requests
from datetime import datetime, timezone, timedelta
import csv
import os
import time

# Defina as suas credenciais da API
USERNAMES = ['fiap_souza_fabiano', 'faculdadedetecnologiadapaulista_junior_fabian']
PASSWORDS = ['4d4J2S4pRn', 'A42f4gzUFE']

# Coordenadas dos postos
postos = {
    "Zona Norte": {
        "Penha": "-23.550520,-46.633308",
        "Perus": "-23.550520,-46.633308",
        "Pirituba": "-23.550520,-46.633308",
        "Freguesia do Ó": "-23.550520,-46.633308",
        "Santana - Tucuruvi": "-23.550520,-46.633308",
        "Tremembé": "-23.550520,-46.633308",
        "São Miguel Paulista": "-23.550520,-46.633308",
        "Itaim Paulista": "-23.550520,-46.633308"
    },
    "Zona Leste": {
        "São Mateus": "-23.550520,-46.633308",
        "Itaquera": "-23.550520,-46.633308",
        "Vila Prudente": "-23.550520,-46.633308",
        "Vila Maria - Guilherme": "-23.550520,-46.633308",
        "Vila Formosa": "-23.550520,-46.633308"
    },
    "Zona Sul": {
        "Ipiranga": "-23.550520,-46.633308",
        "Santo Amaro": "-23.550520,-46.633308",
        "M Boi Mirim": "-23.550520,-46.633308",
        "Cidade Ademar": "-23.550520,-46.633308",
        "Barragem Parelheiros": "-23.550520,-46.633308",
        "Marsilac": "-23.550520,-46.633308"
    },
    "Zona Oeste": {
        "Butantã": "-23.550520,-46.633308",
        "Lapa": "-23.550520,-46.633308",
        "Campo Limpo": "-23.550520,-46.633308",
        "Capela do Socorro - Subprefeitura": "-23.550520,-46.633308",
        "Capela do Socorro": "-23.550520,-46.633308",
        "Pinheiros": "-23.550520,-46.633308"
    },
    "Zona Central": {
        "Sé - CGE": "-23.550520,-46.633308",
        "Móoca": "-23.550520,-46.633308",
        "Vila Mariana": "-23.550520,-46.633308"
    },
    "Grande São Paulo": {
        "Riacho Grande": "-23.550520,-46.633308",
        "Mauá - Paço Municipal": "-23.550520,-46.633308",
        "Santana do Parnaíba": "-23.550520,-46.633308",
        "Jabaquara": "-23.550520,-46.633308"
    }
}
import pytz

# Definir o timezone de Brasília
br_timezone = pytz.timezone('America/Sao_Paulo')

# Obter a data e hora atual no timezone UTC
start_date_utc = datetime.now(timezone.utc)

def save_to_csv(zone, post_name, data):
    # Criar o diretório se não existir
    dir_path = f'previsao/{zone}/'
    os.makedirs(dir_path, exist_ok=True)

    file_path = os.path.join(dir_path, f'{post_name}.csv')

    # Escrever os dados no CSV com o cabeçalho correto
    with open(file_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Chuva(mm)', 'Temp(oC)', 'Umid.Rel.(%)', 'Vel.VT(m/s)', 'Dir.VT(o)', 'Pressão(mb)', 'Data', 'Hora'])

        for row in data:
            writer.writerow(row)

def fetch_data_for_post(post_name, location):
    # Data e hora atuais no formato UTC
    start_date = start_date_utc.astimezone(br_timezone) + timedelta(hours=1)
    end_date = start_date + timedelta(days=1)

    # Converter as datas para o formato ISO 8601
    start_date_str = start_date.strftime('%Y-%m-%dT%H:%M:%SZ')
    end_date_str = end_date.strftime('%Y-%m-%dT%H:%M:%SZ')

    # Intervalo de 1 hora
    time_step = 'PT1H'

    # Parâmetros necessários (sem umidade relativa e direção do vento)
    parameters = 't_2m:C,precip_1h:mm,wind_speed_10m:ms,msl_pressure:hPa'
    response_format = 'json'

    # Construir a URL da API
    url = f'https://api.meteomatics.com/{start_date_str}--{end_date_str}:{time_step}/{parameters}/{location}/{response_format}'

    # Tentar com diferentes credenciais
    for username, password in zip(USERNAMES, PASSWORDS):
        try:
            response = requests.get(url, auth=(username, password))

            if response.status_code == 200:
                data = response.json()
                extracted_data = []

                dates = [entry['date'] for entry in data['data'][0]['coordinates'][0]['dates']]
                temperature_values = [entry['value'] for entry in data['data'][0]['coordinates'][0]['dates']]
                precipitation_values = [entry['value'] for entry in data['data'][1]['coordinates'][0]['dates']]
                wind_speed_values = [entry['value'] for entry in data['data'][2]['coordinates'][0]['dates']]
                pressure_values = [entry['value'] for entry in data['data'][3]['coordinates'][0]['dates']]

                # Formatar os dados para o CSV com os campos vazios onde faltam dados
                for i in range(len(dates)):
                    extracted_data.append([
                        precipitation_values[i],  # Chuva(mm)
                        temperature_values[i],  # Temp(oC)
                        "",  # Umid.Rel.(%) - vazio
                        round(float(wind_speed_values[i]), 2),  # Vel.VT(m/s)
                        "",  # Dir.VT(o) - vazio
                        pressure_values[i],  # Pressão(mb)
                        dates[i][:10],  # Data
                        dates[i][11:13] + ":00"  # Hora ajustada para número cheio
                    ])

                return extracted_data
            else:
                print(f'Erro ao obter dados para o posto {post_name}: {response.status_code}')
                print(response.text)
        except Exception as e:
            print(f'Erro ao tentar acessar a API: {e}')

    return None

def main():
    while True:
        for zone, posts in postos.items():
            for post_name, location in posts.items():
                print(f'Obtendo dados para {post_name} na {zone}')
                data = fetch_data_for_post(post_name, location)
                if data:
                    save_to_csv(zone, post_name, data)
                    print(f'Dados salvos para o posto {post_name}')
                else:
                    print(f'Falha ao obter dados para o posto {post_name}')

        # Esperar 24 horas antes de repetir
        time.sleep(86400)  # 86400 segundos = 24 horas

if __name__ == "__main__":
    main()