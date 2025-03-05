from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
import math
import json
import oracledb
import os
from sqlalchemy import create_engine, text

# Configurações do Selenium
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.binary_location = "local do disco em que o chrome se encontra" --utilizar somente se quiser usar um chrome de versao especifica
chrome_service = Service('chromedriver.exe')

# Configuração do Oracle Client e SQLAlchemy
os.environ["TNS_ADMIN"] = "C:\\Wallet_ORACLEDB"
oracledb.init_oracle_client(lib_dir="C:\\oracle\\instantclient_23_5")
engine = create_engine('oracle+oracledb://--user--:--Password--#@ORACLEDB_high')

# URL base para scraping
BASE_URL = "https://www.cgesp.org/v3/estacao.jsp?POSTO={}"

def load_postos():
    try:
        with open('postoswebScraping.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
            return data
    except Exception as e:
        print(f"Erro ao carregar o arquivo JSON: {e}")
        return {}

# Carrega os dados dos postos
postos = load_postos()
if not postos:
    print("Nenhum dado de postos carregado. Encerrando o script.")
    exit()

def get_driver():
    return webdriver.Chrome(service=chrome_service, options=chrome_options)

driver = get_driver()

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

            if table and len(table.find_all('tr')) > 1:
                rows = table.find_all('tr')
                data = {
                    "qtd_chuva": "",
                    "nr_temp": "",
                    "nr_umid": "",
                    "nr_vel_vt": "",
                    "nr_dir_vt": "",
                    "nr_pressao": "",
                    "data_hora": datetime.now().strftime('%d-%m-%y %H:%M')
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

                # Ajuste a data_hora para o início da hora
                now = datetime.now().replace(minute=0, second=0, microsecond=0)
                data["data_hora"] = now.strftime('%d-%m-%y %H:%M')

                print(f"Tabela encontrada em {station_url}. Dados extraídos: {data}")
                return [data]  # Retorna uma lista contendo o dicionário

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
                    "data_hora": datetime.now().strftime('%d-%m-%y %H:%M')
                }
                # Ajuste a data_hora para o início da hora
                now = datetime.now().replace(minute=0, second=0, microsecond=0)
                data["data_hora"] = now.strftime('%d-%m-%y %H:%M')
                return [data]  # Retorna uma lista contendo o dicionário
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
        '': None
    }

    direction = direction.strip().upper()
    return wind_directions.get(direction, None)


def extract_cod_posto(station_name):
    for region, stations in postos.items():
        for code, name in stations.items():
            if name == station_name:
                return code
    return None

def wait_until_next_hour():
    now = datetime.now()
    next_hour = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
    wait_time = (next_hour - now).total_seconds()
    return wait_time

def get_last_id_clima():
    query = text("SELECT NVL(MAX(id_clima), 0) FROM t_ds_clima_atual")
    with engine.connect() as connection:
        result = connection.execute(query).fetchone()
        last_id_clima = result[0] if result[0] is not None else 0
    return last_id_clima + 1  # Inicia em 1 se a tabela estiver vazia


def save_to_db(data, cod_posto, last_id_clima):
    try:
        qtd_chuva = float(data['qtd_chuva']) if data['qtd_chuva'] else None
        nr_temp = float(data['nr_temp']) if data['nr_temp'] else None
        nr_umid = float(data['nr_umid'].replace('%', '')) if data['nr_umid'] else None
        nr_vel_vt = float(data['nr_vel_vt']) if data['nr_vel_vt'] else None
        nr_dir_vt = wind_direction_to_degrees(data['nr_dir_vt']) if data['nr_dir_vt'] else None
        nr_pressao = float(data['nr_pressao']) if data['nr_pressao'] else None

        # Ajustar para a hora completa no início da hora
        data_hora = datetime.strptime(data['data_hora'], '%d-%m-%y %H:%M')
        data_hora = data_hora.replace(second=0, microsecond=0)  # Definir segundos e microssegundos para 0
        data_hora_str = data_hora.strftime('%d-%m-%y %H:%M')  # Formatar como string para o banco

        with engine.connect() as connection:
            query = text(""" 
                INSERT INTO t_ds_clima_atual (id_clima, cod_posto, qtd_chuva, nr_temp, nr_umid, nr_vel_vt, nr_dir_vt, nr_pressao, data_hora) 
                VALUES (:id_clima, :cod_posto, :qtd_chuva, :nr_temp, :nr_umid, :nr_vel_vt, :nr_dir_vt, :nr_pressao, TO_TIMESTAMP(:data_hora, 'DD-MM-YY HH24:MI'))
            """)

            if cod_posto:
                connection.execute(query, {
                    'id_clima': last_id_clima,
                    'cod_posto': cod_posto,
                    'qtd_chuva': qtd_chuva,
                    'nr_temp': nr_temp,
                    'nr_umid': nr_umid,
                    'nr_vel_vt': nr_vel_vt,
                    'nr_dir_vt': nr_dir_vt,
                    'nr_pressao': nr_pressao,
                    'data_hora': data_hora_str
                })
                connection.execute(text('COMMIT'))
                print(f"Dados salvos no banco para o posto {cod_posto} (ID Clima: {last_id_clima})")
            else:
                print(f"Cod posto vazio para {data['data_hora']}")
    except Exception as e:
        print(f"Erro ao salvar os dados no banco: {e}")


def process_station_data(station_url, station_name, last_id_clima):
    data = get_station_data(station_url)
    if data:
        cod_posto = extract_cod_posto(station_name)

        if cod_posto is None:
            print(f"Erro: código do posto não encontrado para a estação {station_name}.")
            return

        data[0]['cod_posto'] = cod_posto

        save_to_db(data[0], cod_posto, last_id_clima)

def main():
    last_id_clima = get_last_id_clima()
    print(f"Iniciando o processo com ID Clima inicial: {last_id_clima}")
    while True:
        for region, stations in postos.items():
            print(f"Processando a região {region}")
            for station_code, station_name in stations.items():
                station_url = BASE_URL.format(station_code)
                process_station_data(station_url, station_name, last_id_clima)
                last_id_clima += 1

        sleep_time = wait_until_next_hour()
        print(f"Aguardando {math.ceil(sleep_time)} segundos até o próximo horário.")
        time.sleep(sleep_time)

if __name__ == "__main__":
    main()
