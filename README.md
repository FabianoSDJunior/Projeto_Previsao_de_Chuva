# 🌧️ Projeto Final - Challenge Minsait (FIAP)

## 📹 Apresentação em Vídeo
👉 [Assista no YouTube](https://youtu.be/g3v8oBnwTHE)

## 📋 Sobre o Projeto
Projeto desenvolvido no Challenge da Minsait, integrando dados climáticos, de alagamentos e interrupções de energia. O objetivo do projeto foi comparar dados históricos de cada região com os dados atuais, atualizando-os a cada 1 hora. Após identificar padrões, utilizamos essas informações para detectar quedas de luz e alagamentos nas ruas. Foi feita toda a pipeline de dados: desde a extração (web scraping e API), passando por tratamento e análise, até a construção de indicadores preditivos e visualizações.

## 🔗 Tecnologias Utilizadas
- Python (Pandas, Requests, Selenium)
- Banco de Dados: Oracle Cloud
- Web Scraping (CGESP e outros)
- Visualizações: Streamlit

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

## 📊 Resultados
- Previsão de chuva e risco de alagamentos com base em dados históricos.
- Detecção de quedas de luz e alagamentos com base na comparação de dados históricos e atuais.
- Painel de monitoramento em tempo real com integração de dados externos.
- Análise histórica para identificar padrões climáticos e tendências.

---

## 🔄 Etapas do Projeto

### 1. **Coleta de Dados**
A coleta de dados é realizada por meio de dois principais métodos:
- **Web Scraping**: Utilizando Selenium e Requests, os dados de alagamentos e condições climáticas são extraídos de sites como a CGESP e outras fontes. Estes dados incluem informações sobre chuvas e alagamentos, que são armazenadas temporariamente em arquivos JSON.
- **API**: A previsão do tempo é obtida por meio de uma API, onde as informações climáticas são recuperadas, como a previsão de chuva, temperatura e umidade.

### 2. **Armazenamento dos Dados**
Após a coleta, os dados são armazenados:
- **JSON**: Durante o processo de scraping, os dados são temporariamente armazenados em arquivos JSON para garantir a integridade antes do envio para o banco de dados.
- **Oracle Cloud DB**: Uma vez que os dados são limpos e estruturados, eles são enviados para um banco de dados Oracle Cloud, onde ficam acessíveis para futuras análises e visualizações.

### 3. **Tratamento de Dados**
Os dados coletados e armazenados são processados para garantir sua qualidade e integridade. As principais etapas de tratamento incluem:
- **Limpeza**: Remoção de valores faltantes ou duplicados nos dados de chuva, temperatura, umidade e outros parâmetros relevantes.
- **Transformação**: Convertem-se os dados de formato bruto para tabelas estruturadas, permitindo a análise estatística e a criação de indicadores preditivos.
- **Cálculos de Probabilidade**: A probabilidade de alagamento e de falha energética é calculada com base em dados históricos de chuva e outras variáveis.

### 4. **Comparação de Dados Históricos e Atuais**
A cada 1 hora, comparamos os dados atuais com os históricos de cada região para identificar padrões. Quando um padrão é detectado, ele é usado para prever e alertar sobre possíveis quedas de luz ou alagamentos nas ruas.

### 5. **Visualização no Dashboard**
As visualizações são apresentadas por meio de um painel interativo no **Streamlit**, com o seguinte objetivo:
- **Gráficos de Linhas e Barras**: Exibem a quantidade de chuvas ao longo do tempo e o risco de alagamentos em diferentes regiões.
- **Mapas de Calor**: Apresentam a intensidade da chuva e o risco de falha energética por localização.
- **Tabelas de Resumo**: Mostram dados históricos e estatísticas como médias, desvios padrão e outras métricas importantes para cada estação.
- **Indicadores Preditivos**: Calculam e exibem a probabilidade de eventos climáticos extremos (como alagamentos ou falhas de energia) para os próximos dias.

---

### 💼 Contato
[LinkedIn](https://www.linkedin.com/in/fabsdjr/) | [E-mail](mailto:fabdamiao@outlook.com)

---

## 📂 Detalhamento dos Scripts

### 1. **Web Scraping - Dados de Alagamentos**
Coletamos dados de alagamentos em tempo real através de web scraping utilizando Selenium e Requests. Esses dados são armazenados em arquivos JSON antes de serem carregados no banco de dados Oracle Cloud.

### 2. **Consumo de API para Previsão do Tempo**
Utilizamos uma API externa para obter dados de previsão do tempo, como chuvas, temperaturas e umidade. Esses dados são processados e armazenados para posterior análise.

### 3. **Integração com Oracle DB**
Os dados extraídos são armazenados no Oracle Cloud Database, onde são integrados com outros dados históricos para análises preditivas e relatórios em tempo real.

### 4. **Comparação de Dados e Detecção de Padrões**
Os dados atuais são comparados com os históricos de cada região, atualizando a cada 1 hora. Quando um padrão de risco é detectado, ele é usado para prever alagamentos e quedas de luz nas ruas.

### 5. **Visualizações no Dashboard**
A partir dos dados tratados, criamos gráficos interativos utilizando Streamlit. O painel de visualização permite monitorar em tempo real o risco de alagamentos e interrupções de energia, além de apresentar uma análise histórica de padrões climáticos.
