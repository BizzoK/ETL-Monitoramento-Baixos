import sqlite3
import pandas as pd

conexao = sqlite3.connect('historico_precos.db')

query = "SELECT Modelo_Padronizado, Preco_Limpo, Link FROM historico WHERE `Preco_Limpo` < 1500"
df_baratos = pd.read_sql_query(query, conexao)
conexao.close()

print(df_baratos)