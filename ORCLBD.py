import pandas as pd
import oracledb
from sqlalchemy import create_engine
import os
# Defina a variável TNS_ADMIN para o diretório da Wallet
os.environ["TNS_ADMIN"] = "C:\\Wallet_ORACLEDB"

# Inicialize o Oracle Client
oracledb.init_oracle_client(lib_dir="C:\\oracle\\instantclient_23_5")

# Crie a engine SQLAlchemy
engine = create_engine('oracle+oracledb://admin:Abacate1#Espacial1#@ORACLEDB_high')

# Conecte-se ao banco de dados e leia a tabela em um DataFrame
with engine.connect() as connection:
    query = "SELECT * FROM T_DS_POSTO"  # Substitua 'sua_tabela' pelo nome da tabela desejada
    df = pd.read_sql(query, connection)

# Exiba o DataFrame
print(df)



