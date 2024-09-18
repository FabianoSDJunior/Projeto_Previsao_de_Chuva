from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time

# Configurações do Selenium
chrome_options = Options()
#chrome_options.add_argument("--headless")
chrome_options.binary_location = "C:\\Users\\fabda\\Documents\\chrome-win64\\chrome.exe"
chrome_service = Service('chromedriver.exe')

def get_driver():
    return webdriver.Chrome(service=chrome_service, options=chrome_options)

driver = get_driver()

# --------------------------------------------
# Seção para configuração de datas
# Data de Início
ano_inicio = 2020
mes_inicio = 1
dia_inicio = 2

# Data de Término
ano_fim = 2020
mes_fim = 1
dia_fim = 4
# --------------------------------------------

def format_date(dia, mes, ano):
    return f"{dia:02}/{mes:02}/{ano}"

def get_url(dia, mes, ano):
    return f"https://www.cgesp.org/v3/alagamentos.jsp?dataBusca={format_date(dia, mes, ano)}&enviaBusca=Buscar"

def get_flood_data(url, dia, mes, ano):
    global driver
    try:
        driver.get(url)

        time.sleep(2)

        # Busca pelo conteúdo da tabela
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        tables = soup.find_all('table')  # Encontrar todas as tabelas

        # Imprime a data no formato desejado
        print(f"\nDados do dia: {format_date(dia, mes, ano)}")

        if tables:
            for index, table in enumerate(tables):
                print(f"\nTabela {index + 1} encontrada:")
                rows = table.find_all('tr')
                for row in rows:
                    columns = row.find_all('td')
                    data = [col.text.strip() for col in columns]
                    print(data)  # Visualizar os dados da tabela
        else:
            print(f"Não há registros de alagamentos.")

    except Exception as e:
        print(f"Erro ao carregar os dados: {e}")

# Função para incrementar a data
def increment_date(dia, mes, ano):
    date = datetime(ano, mes, dia) + timedelta(days=1)
    return date.day, date.month, date.year

# Varredura das datas entre o início e o fim
def scrape_dates(dia_inicio, mes_inicio, ano_inicio, dia_fim, mes_fim, ano_fim):
    dia, mes, ano = dia_inicio, mes_inicio, ano_inicio
    while (ano < ano_fim) or (ano == ano_fim and (mes < mes_fim or (mes == mes_fim and dia <= dia_fim))):
        url = get_url(dia, mes, ano)
        get_flood_data(url, dia, mes, ano)
        dia, mes, ano = increment_date(dia, mes, ano)

scrape_dates(dia_inicio, mes_inicio, ano_inicio, dia_fim, mes_fim, ano_fim)

