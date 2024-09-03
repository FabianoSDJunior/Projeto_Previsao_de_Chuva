from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium import webdriver


# Configurações do Selenium
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.binary_location = "C:\\Users\\fabda\\Documents\\chrome-win64\\chrome.exe"
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



from bs4 import BeautifulSoup
from datetime import datetime
import time

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
                    "Chuva(mm)": "",
                    "Temp(oC)": "",
                    "Umid.Rel.(%)": "",
                    "Vel.VT(m/s)": "",
                    "Dir.VT(o)": "",
                    "Pressão(mb)": "",
                    "Data": datetime.now().strftime('%Y-%m-%d'),
                    "Hora": datetime.now().strftime('%H:00')
                }

                for row in rows:
                    columns = row.find_all('td')
                    if len(columns) == 2:
                        key, value = columns[0].text.strip(), columns[1].text.strip()
                        if key.startswith("Per. Atual"):
                            data["Chuva(mm)"] = value.split()[0]
                        elif key.startswith("Atual:") and "ºC" in value:
                            data["Temp(oC)"] = value.split()[0]
                        elif key.startswith("Atual:") and "%" in value:
                            data["Umid.Rel.(%)"] = value.split()[0]
                        elif key.startswith("Direção:"):
                            data["Dir.VT(o)"] = value
                        elif key.startswith("Velocidade:"):
                            data["Vel.VT(m/s)"] = f"{float(value.split()[0].replace('km/h', '')) * 1000 / 3600:.2f}"
                        elif key.startswith("Atual:") and "hPa" in value:
                            data["Pressão(mb)"] = value.split()[0]

                print(f"Tabela encontrada em {station_url}. Dados extraídos.")
                return data

            else:
                print(f"Nenhuma tabela encontrada ou tabela vazia em {station_url}.")
                return None

        except Exception as e:
            print(f"Erro ao carregar os dados: {e}")
            if attempt == retries - 1:

                data = {
                    "Chuva(mm)": "",
                    "Temp(oC)": "",
                    "Umid.Rel.(%)": "",
                    "Vel.VT(m/s)": "",
                    "Dir.VT(o)": "",
                    "Pressão(mb)": "",
                    "Data": datetime.now().strftime('%Y-%m-%d'),
                    "Hora": datetime.now().strftime('%H:00')
                }
                return data
            else:
                driver.quit()
                driver = get_driver()
                time.sleep(10)

    return None



import pandas as pd
import os

def save_to_csv(zone, station_name, data):
    if data:
        file_path = f'clima_SP_zonas/{zone}/{station_name}.csv'

        data["Posto"] = station_name

        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        df = pd.DataFrame([data])

        df.to_csv(file_path, mode='a', index=False, header=not os.path.exists(file_path),sep=';')



import schedule

def run_scraping():
    for zone, stations in postos.items():
        for station_code, station_name in stations.items():
            station_url = BASE_URL.format(station_code)
            station_name_with_code = f"posto {station_code} - {station_name}"

            data = get_station_data(station_url)
            save_to_csv(zone, station_name_with_code, data)

# Agende o script para rodar a cada hora cheia
for hour in range(24):
    schedule_time = f"{hour:02d}:00"
    schedule.every().day.at(schedule_time).do(run_scraping)

# Loop infinito para manter o agendamento ativo
while True:
    schedule.run_pending()
    time.sleep(1)