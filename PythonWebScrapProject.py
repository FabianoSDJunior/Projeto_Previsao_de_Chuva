from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time
import os
from datetime import datetime, timedelta
import math

# Configurações do Selenium
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.binary_location = "local do disco em que o chrome se encontra" --utilizar somente se quiser usar um chrome de versao especifica
chrome_service = Service('chromedriver.exe')


def get_driver():
    return webdriver.Chrome(service=chrome_service, options=chrome_options)


driver = get_driver()

BASE_URL = "https://www.cgesp.org/v3/estacao.jsp?POSTO={}"

postos = {
    "Zona Norte": {
        "504": "Perus",
        "515": "Pirituba",
        "509": "Freguesia do Ó",
        "510": "Santana - Tucuruvi",
        "1000944": "Tremembé",
        "540": "Vila Maria - Guilherme"
    },
    "Zona Sul": {
        "1000852": "Santo Amaro",
        "1000850": "M Boi Mirim",
        "592": "Cidade Ademar",
        "507": "Barragem Parelheiros",
        "1000300": "Marsilac",
        "1000854": "Campo Limpo",
        "846": "Capela do Socorro - Subprefeitura",
        "1000857": "Capela do Socorro",
        "495": "Vila Mariana",
        "634": "Jabaquara",
        "400": "Riacho Grande"
    },
    "Zona Leste": {
        "1000887": "Penha",
        "1000862": "São Miguel Paulista",
        "1000882": "Itaim Paulista",
        "1000859": "Vila Formosa",
        "1000864": "Itaquera",
        "524": "Vila Prudente",
        "1000876": "Mauá - Paço Municipal"
    },
    "Zona Oeste": {
        "1000842": "Butantã",
        "1000848": "Lapa",
        "1000635": "Pinheiros",
        "1000880": "Santana do Parnaíba"
    },
    "Centro": {
        "503": "Sé - CGE",
        "1000840": "Ipiranga",
        "1000860": "Móoca"
    }
}


def get_station_data(station_url, retries=3, page_timeout=30):
    global driver
    for attempt in range(retries):
        try:
            time.sleep(8)
            driver.set_page_load_timeout(page_timeout)
            driver.get(station_url)

            WebDriverWait(driver, page_timeout).until(
                lambda d: d.execute_script('return document.readyState') == 'complete'
            )

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, 'table'))
            )

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            table = soup.find('table')

            # Verificar se a tabela foi encontrada e tem linhas
            if table and len(table.find_all('tr')) > 1:
                rows = table.find_all('tr')

                # Extraindo os dados da tabela
                data = {
                    "qtd_chuva": "",
                    "nr_temp": "",
                    "nr_umid": "",
                    "nr_vel_vt": "",
                    "nr_dir_vt": "",
                    "nr_pressao": "",
                    "data_hora": datetime.now().strftime('%d-%m-%y %H:00')
                }

                for row in rows:
                    columns = row.find_all('td')
                    if len(columns) == 2:
                        key, value = columns[0].text.strip(), columns[1].text.strip()
                        if key.startswith("Per. Atual"):
                            data["qtd_chuva"] = value.split()[0]
                        elif key.startswith("Atual:") and "ºC" in value:
                            data["nr_temp"] = value.split()[0]
                        elif key.startswith("Atual:") and "%" in value:
                            data["nr_umid"] = value.split()[0]
                        elif key.startswith("Direção:"):
                            data["nr_dir_vt"] = value
                        elif key.startswith("Velocidade:"):
                            data["nr_vel_vt"] = f"{float(value.split()[0].replace('km/h', '')) * 1000 / 3600:.2f}"
                        elif key.startswith("Atual:") and "hPa" in value:
                            data["nr_pressao"] = value.split()[0]

                print(f"Tabela encontrada em {station_url}. Dados extraídos.")
                return data

            else:
                print(f"Nenhuma tabela encontrada ou tabela vazia em {station_url}.")
                return None

        except Exception as e:
            print(f"Erro ao carregar os dados: {e}")
            if attempt == retries - 1:
                data = {
                    "qtd_chuva": "",
                    "nr_temp": "",
                    "nr_umid": "",
                    "nr_vel_vt": "",
                    "nr_dir_vt": "",
                    "nr_pressao": "",
                    "data_hora": datetime.now().strftime('%d-%m-%y %H:00')
                }
                return data
            else:
                driver.quit()
                driver = get_driver()
                time.sleep(10)

    return None


def wind_direction_to_degrees(direction):
    wind_directions = {
        'N': 0.0, 'NNE': 22.5, 'NE': 45.0, 'ENE': 67.5,
        'E': 90.0, 'ESE': 112.5, 'SE': 135.0, 'SSE': 157.5,
        'S': 180.0, 'SSW': 202.5, 'SW': 225.0, 'WSW': 247.5,
        'W': 270.0, 'WNW': 292.5, 'NW': 315.0, 'NNW': 337.5,
        '': None  # Para valores em branco, retornamos None
    }

    # Converter para maiúsculas e remover espaços extras
    direction = direction.strip().upper()

    # Retornar o grau correspondente ou None se não encontrado
    return wind_directions.get(direction, None)


def update_wind_directions(data):
    if data["nr_dir_vt"]:
        degrees = wind_direction_to_degrees(data["nr_dir_vt"])
        if degrees is not None:
            data["nr_dir_vt"] = f"{degrees:000.1f}"
        else:
            data["nr_dir_vt"] = "N/A"  # ou algum valor padrão para direções desconhecidas
    return data


def save_to_csv(zone, station_name, data):
    if data:
        # Atualize a direção do vento antes de salvar
        data = update_wind_directions(data)

        file_path = f'clima_SP_zonas/{zone}/{station_name}.csv'

        data["Posto"] = station_name

        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        df = pd.DataFrame([data])

        df.to_csv(file_path, mode='a', index=False, header=not os.path.exists(file_path), sep=';')


def wait_until_next_hour():
    now = datetime.now()
    next_hour = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
    wait_time = (next_hour - now).total_seconds()
    return wait_time


def wait_until_next_hour():
    now = datetime.now()
    next_hour = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
    wait_time = (next_hour - now).total_seconds()
    return wait_time

while True:
    for zone, stations in postos.items():
        for station_code, station_name in stations.items():
            station_url = BASE_URL.format(station_code)
            station_name_with_code = f"posto {station_code} - {station_name}"

            data = get_station_data(station_url)

            save_to_csv(zone, station_name_with_code, data)

    # Calcule o tempo restante até a próxima hora cheia
    sleep_time = wait_until_next_hour()
    print(f"Aguardando {math.ceil(sleep_time)} segundos até o próximo horário.")
    time.sleep(sleep_time)

