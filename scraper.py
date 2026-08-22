import sys
import time
import pandas as pd
import sqlite3
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from rapidfuzz import process, fuzz
from datetime import date
sys.stdout.reconfigure(encoding='utf-8')
# ------------------------------------------------------------------------------------------
# EXTRAÇÃO - COLETANDO OS DADOS COM SELENIUM

time.sleep(5)
print("Ligando o robô...")
print("Iniciando o ChromeDriver...", flush=True)
servico = Service(ChromeDriverManager().install())
opcoes = webdriver.ChromeOptions()
#opcoes.add_argument('--headless')  # Executa o Chrome em modo headless (sem interface gráfica)
navegador = webdriver.Chrome(service=servico, options=opcoes)

url = 'https://lista.mercadolivre.com.br/instrumentos-musicais/baixo-tagima'
navegador.get(url)

lista_produtos = []
total_paginas = 5
print(f"Total de páginas a serem lidas: {total_paginas}")

for pagina in range(1, total_paginas + 1):
    print(f"\nPágina {pagina} carregada! Lendo os dados...")
    time.sleep(3)

    soup = BeautifulSoup(navegador.page_source, 'html.parser')
    anuncios = soup.find_all('li', class_='ui-search-layout__item')
    print(f"Encontramos {len(anuncios)} anúncios na página.")

    for anuncio in anuncios:
        titulo_tag = anuncio.find('a', class_='poly-component__title') or anuncio.find('h3')
        titulo = titulo_tag.text if titulo_tag else 'Sem título'

        link = titulo_tag['href'] if (titulo_tag and titulo_tag.has_attr('href')) else 'Sem link'
        preco_tag = anuncio.find('span', class_='andes-money-amount__fraction')
        preco = preco_tag.text if preco_tag else '0'
        
        lista_produtos.append({'Modelo_Original': titulo, 'Preco_Bruto': preco, 'Link': link})

    # clique na próxima página usando JS direto no DOM
    if pagina < total_paginas: 
        try:
            # acha a tag <a> usando o atributo de controle exato que vimos na sua imagem
            botao_proxima = navegador.find_element(By.CSS_SELECTOR, 'a[data-andes-pagination-control="next"]')
            
            # força o clique via JavaScript, ignorando qualquer banner por cima
            navegador.execute_script("arguments[0].click();", botao_proxima)
            
            print(f"Clicou e carregando a página {pagina + 1}...")
        except Exception as erro:
            print("Fim do catálogo ou botão não encontrado.")
            break

navegador.quit()

# Criando o DataFrame
df = pd.DataFrame(lista_produtos)

if df.empty:
    print("Nenhum produto encontrado! O robô foi bloqueado pelo Mercado Livre.")
    import sys
    sys.exit(0)
    
print("\n=== BASE DE DADOS BRUTA ===")
print(df)


# ------------------------------------------------------------------------------------------
# TRANSFORMAÇÃO - PADRONIZANDO COM RAPIDFUZZ
print("\nPadronizando os modelos com RapidFuzz...")

# Limpeza do preço
df['Preco'] = df['Preco_Bruto'].str.replace('.', '').str.replace(',', '.').astype(float)

# Lista Mestra
modelos_oficiais = [
    "Tagima TW-65",
    "Tagima TW-66",
    "Tagima TW-73",
    "Tagima MB-50",
    "Tagima Millenium 4",
    "Tagima Millenium 5",
    "Tagima TBM-5",
    "Tagima TBM-4",
    "Tagima Tjb-5",
    "Tagima Tjb-4"
]

# Função Estatística
def padronizar_com_fuzz(nome_sujo):
    # process.extractOne compara o título do anúncio com a Lista Mestra
    # devolve uma tupla: (Melhor nome, Score de similaridade, Índice da lista)
    melhor_match = process.extractOne(
        nome_sujo.lower(),
        [m.lower() for m in modelos_oficiais],
        scorer=fuzz.token_set_ratio # procura a intersecção das palavras, reorganiza as palavras na memória e ignora a ordem 
    )

    #[0] = melhor nome, [1] = score, [2] = índice da lista
    # se a probabilidade for maior ou igual a 55%, assumimos o match
    if melhor_match and melhor_match[1] >= 90:
        # puxa o nome oficial da lista mestra usando o índice do melhor match
        return modelos_oficiais[melhor_match[2]]
    else:
        return 'Outros modelos'

df['Modelo_Padronizado'] = df['Modelo_Original'].apply(padronizar_com_fuzz)
df['Data_Coleta'] = date.today().strftime('%d/%m/%Y')


pd.set_option('display.max_columns', None)
pd.set_option('display.expand_frame_repr', False) # impede-a de quebrar a linha


df_final = df[['Modelo_Padronizado', 'Preco', 'Link', 'Data_Coleta', 'Modelo_Original']]

print("\n=== BASE DE DADOS FINAL ===")
print(df_final)


# ------------------------------------------------------------------------------------------
# CARGA - LOAD PARA SQLITE

# SQLite cria esse arquivo fisicamente na pasta se ele não existir
conexao = sqlite3.connect('historico_precos.db')

# if_exists='replace' para que ele zere a tabela a cada teste.
# quando para produção, mudaremos para 'append' para acumular o histórico.
df_final.to_sql('historico', con=conexao, if_exists='append', index=False)
print("Dados salvos com sucesso na tabela.")
conexao.close()
