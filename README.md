# 🌧️ Projeto Final - Challenge Minsait (FIAP)

## 📹 Apresentação em Vídeo
👉 [Assista no YouTube](coloque_o_link_aqui)

## 📋 Sobre o Projeto
Projeto desenvolvido no Challenge da Minsait, integrando dados climáticos, de alagamentos e interrupções de energia. Foi feita toda a pipeline de dados: desde a extração (web scraping e API), passando por tratamento e análise, até a construção de indicadores preditivos e visualizações.

## 🔗 Tecnologias Utilizadas
- Python (Pandas, Requests, Selenium)
- Banco de Dados: Oracle Cloud
- APIs de clima (WeatherAPI)
- Web Scraping (CGESP e outros)
- Visualizações: Matplotlib, Seaborn

## 📂 Estrutura do Repositório
| Arquivo                    | Descrição |
|-------------------|------------------|
| ORCLBD.py                   | Conexão com OracleDB |
| ProjetoFinalChallenge.py   | Script principal do projeto |
| PythonWebScrapAlagamentos.py | Web scraping de dados de alagamentos |
| PythonWebScrapProject.py | Atualização de horários via scraping |
| WeatherAPI_Previsao.py | Consumo de API para previsão do tempo |
| WebScrapClimaORACLEDB.py | Pipeline completa clima + OracleDB |
| chromedriver.exe | Dependência para scraping |
| postoswebScraping.json | Configurações para scraping |

---

### 📊 Resultados
- Previsão de chuva e risco de alagamentos com base em dados históricos.
- Painel de monitoramento em tempo real com integração de dados externos.
- Análise histórica para identificar padrões climáticos e tendências.

---

### 💼 Contato
[LinkedIn]([https://www.linkedin.com/in/fabsdjr/]) | [E-mail](mailto:fabdamiao@outlook.com)

---

### 2️⃣ Dentro de cada pasta (se separar por tema ou script), você pode ter um README menor explicando o código específico

Exemplo para a pasta de WebScrapClima:

```markdown
# 🌦️ Web Scraping - Clima CGESP

## Objetivo
Coletar dados em tempo real do site CGESP sobre chuvas e disponibilizar no Oracle Cloud para análises.

## Principais Tecnologias
- Python (Requests, BeautifulSoup, Selenium)
- OracleDB (oracledb)
- JSON para armazenamento temporário

## Fluxo
1. Coleta via Web Scraping
2. Salvamento em JSON
3. Upload no OracleDB
