from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from datetime import datetime, timedelta
from selenium import webdriver
from bs4 import BeautifulSoup
import time
import csv
import os
import re


# Configurações do Selenium
chrome_options = Options()
chrome_options.add_argument("--headless")
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
dia_inicio = 1

# Data de Término
ano_fim = 2024
mes_fim = 8
dia_fim = 31
# --------------------------------------------

def format_date(dia, mes, ano):
    return f"{dia:02}/{mes:02}/{ano}"

def get_url(dia, mes, ano):
    return f"https://www.cgesp.org/v3/alagamentos.jsp?dataBusca={format_date(dia, mes, ano)}&enviaBusca=Buscar"

def extract_data_from_text(text, posto, data_inicio):
    data = {
        'cod_posto': '',
        'Posto': posto,
        'Local': '',
        'Sentido': '',
        'Referencia': '',
        'data_inicio': '',
        'data_termino': ''
    }

    # Extrair hora de início e término
    start_time_match = re.search(r'(?<=De\s)(\d{2}:\d{2})', text)
    end_time_match = re.search(r'(?<=a\s)(\d{2}:\d{2})', text)

    if start_time_match:
        start_time = start_time_match.group(1)
        data['data_inicio'] = f"{data_inicio} {start_time}"

    if end_time_match:
        end_time = end_time_match.group(1)
        start_datetime = datetime.strptime(data['data_inicio'], '%d/%m/%Y %H:%M')
        end_datetime = datetime.strptime(f"{data_inicio} {end_time}", '%d/%m/%Y %H:%M')

        if end_datetime <= start_datetime:
            # Se o horário de término é menor ou igual ao horário de início, adiciona um dia
            end_datetime += timedelta(days=1)

        data['data_termino'] = end_datetime.strftime('%d/%m/%Y %H:%M')

    # Extrair local
    local_match = re.search(r'(?<=De\s\d{2}:\d{2}\sa\s\d{2}:\d{2})\s(.*?)(?=\n\nSentido:|<br\s*/>)', text, re.DOTALL)
    if local_match:
        data['Local'] = local_match.group(1).strip()

    # Extrair sentido
    sense_match = re.search(r'(?<=Sentido:\s)([^\n]+)', text)
    if sense_match:
        data['Sentido'] = sense_match.group(1).strip()

    # Extrair referência
    reference_match = re.search(r'(?<=Referência:\s)(.*)', text)
    if reference_match:
        data['Referencia'] = reference_match.group(1).strip()

    return data

def find_post_code(post_name, post_codes):
    for zone, codes in post_codes.items():
        for code, name in codes.items():
            if name.lower() in post_name.lower():
                return code
    return None

def alagamento(url, dia, mes, ano, post_codes):
    global driver
    try:
        driver.get(url)
        time.sleep(12)

        # Busca pelo conteúdo da tabela
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        tables = soup.find_all('table', class_='tb-pontos-de-alagamentos')

        # Imprime a data no formato desejado
        print(f"\nDados do dia: {format_date(dia, mes, ano)}")

        results = []

        if tables:
            for index, table in enumerate(tables):
                print(f"\nTabela {index + 1} encontrada:")
                bairro = table.find('td', class_='bairro arial-bairros-alag linha-pontilhada')
                if bairro:
                    bairro = bairro.get_text(strip=True)

                rows = table.find_all('tr')
                for row in rows:
                    columns = row.find_all('td')
                    if not columns:
                        continue
                    data_items = row.find_all('div', class_='ponto-de-alagamento')
                    for item in data_items:
                        text = item.get_text(separator='\n')
                        extracted_data = extract_data_from_text(text, bairro, format_date(dia, mes, ano))

                        # Adicionar código do posto
                        post_code = find_post_code(bairro, post_codes)
                        if post_code:
                            extracted_data['cod_posto'] = post_code
                        else:
                            extracted_data['cod_posto'] = 'Desconhecido'

                        results.append(extracted_data)
                        print(extracted_data)
        else:
            print(f"Não há registros de alagamentos.")

        return results

    except Exception as e:
        print(f"Erro ao carregar os dados: {e}")
        return []

# Função para incrementar a data
def increment_date(dia, mes, ano):
    date = datetime(ano, mes, dia) + timedelta(days=1)
    return date.day, date.month, date.year

# Varredura das datas entre o início e o fim
def scrape_dates(dia_inicio, mes_inicio, ano_inicio, dia_fim, mes_fim, ano_fim, post_codes):
    dia, mes, ano = dia_inicio, mes_inicio, ano_inicio

    file_name = 'AlagamentosCGESP.csv'

    while (ano < ano_fim) or (ano == ano_fim and (mes < mes_fim or (mes == mes_fim and dia <= dia_fim))):
        url = get_url(dia, mes, ano)
        daily_results = alagamento(url, dia, mes, ano, post_codes)

        # Salvar os resultados em um arquivo CSV de forma incremental
        if daily_results:
            keys = daily_results[0].keys()
            file_exists = os.path.isfile(file_name)
            with open(file_name, 'a', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=keys)

                # Escreve o cabeçalho apenas se o arquivo não existir
                if not file_exists:
                    writer.writeheader()

                writer.writerows(daily_results)

        dia, mes, ano = increment_date(dia, mes, ano)


# Mapeamento dos códigos dos postos
post_codes = {
    "Zona Norte": {
        "504": "Perus",
        "515": "Pirituba",
        "509": "Freguesia do Ó",
        "510": "Santana",
        "1000944": "Tremembé",
        "540": "Vila Maria/ Vila Guilherme",
    },
    "Zona Sul": {
        "1000852": "Santo Amaro",
        "1000850": "M'Boi Mirim",
        "592": "Cidade Ademar",
        "507": "Parelheiros",
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
        "1000876": "Mauá - Paço Municipal",
        "2222222": 'Ermelino Matarazzo'
    },
    "Zona Oeste": {
        "1000842": "Butantã",
        "1000848": "Lapa",
        "1000635": "Pinheiros",
        "1000880": "Santana do Parnaíba"
    },
    "Centro": {
        "503": "Sé",
        "1000840": "Ipiranga",
        "1000860": "Mooca",
        "1111111": 'Casa Verde'
    }
}

scrape_dates(dia_inicio, mes_inicio, ano_inicio, dia_fim, mes_fim, ano_fim, post_codes)


