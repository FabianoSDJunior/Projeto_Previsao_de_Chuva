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
from datetime import datetime

# Configurações do Selenium
chrome_options = Options()
chrome_options.add_argument("--headless")  # Execute o Chrome em modo headless (sem abrir a janela)
chrome_options.binary_location = "C:\\Users\\fabda\\Documents\\chrome-win64\\chrome.exe"
chrome_service = Service('chromedriver.exe')  # Coloque o caminho correto do chromedriver aqui

def get_driver():
    return webdriver.Chrome(service=chrome_service, options=chrome_options)

driver = get_driver()

# URL base fixo com um placeholder para o número do posto
BASE_URL = "https://www.cgesp.org/v3/estacao.jsp?POSTO={}"

# Dicionário para você adicionar os números dos postos correspondentes a cada zona
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
        "634": "Jabaquara"
    },
    "Zona Leste": {
        "1000887": "Penha",
        "1000862": "São Miguel Paulista",
        "1000882": "Itaim Paulista",
        "1000859": "Vila Formosa",
        "1000864": "Itaquera",
        "524": "Vila Prudente"
    },
    "Zona Oeste": {
        "1000842": "Butantã",
        "1000848": "Lapa",
        "1000635": "Pinheiros"
    },
    "Centro": {
        "503": "Sé - CGE",
        "1000840": "Ipiranga",
        "1000860": "Móoca"
    },
    "Grande SP": {
        "400": "Riacho Grande",
        "1000876": "Mauá - Paço Municipal",
        "1000880": "Santana do Parnaíba"
    }
}

def get_station_data(station_url, retries=3):
    global driver
    for attempt in range(retries):
        try:
            time.sleep(8)
            driver.get(station_url)
            start_time = time.time()

            # Aguardar até que a tabela esteja presente ou timeout de 30 segundos
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.TAG_NAME, 'table'))
            )
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            table = soup.find('table')

            if table:
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
                print(f"Nenhuma tabela encontrada em {station_url}.")
                return None

        except Exception as e:
            print(f"Erro ao carregar os dados: {e}")
            if time.time() - start_time > 30:
                print(f"Reiniciando o driver devido ao timeout...")
                driver.quit()
                driver = get_driver()
            else:
                time.sleep(10)  # Espera antes de tentar novamente
    return None

def save_to_csv(zone, station_name, data):
    if data:
        # Definindo o caminho do arquivo CSV
        file_path = f'clima_SP_zonas/{zone}/{station_name}.csv'


        # Verificando se o diretório existe
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # Convertendo os dados para um DataFrame
        df = pd.DataFrame([data])

        # Salvando no CSV, acrescentando se o arquivo já existir
        df.to_csv(file_path, mode='a', index=False, header=not os.path.exists(file_path))

# Loop para executar o scraping a cada 1 hora
while True:
    for zone, stations in postos.items():
        for station_code, station_name in stations.items():
            station_url = BASE_URL.format(station_code)
            station_name_with_code = f"posto {station_code} - {station_name}"

            # Coletando os dados da estação
            data = get_station_data(station_url)

            # Salvando os dados no CSV correspondente à zona
            save_to_csv(zone, station_name_with_code, data)

    # Aguardar 1 hora (3600 segundos)
    time.sleep(3600)
