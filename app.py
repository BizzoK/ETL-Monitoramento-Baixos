import streamlit as st
import pandas as pd
import sqlite3

st.set_page_config(page_title="Monitor de Baixos Tagima", layout="wide")
st.title("Radar de Preços: Baixos Tagima (Mercado Livre)")

st.markdown("""
    <style>
    .stSelectbox label p {
        font-size: 20px !important;
    }
    .stSlider label p {
            font-size: 20px !important;
        }
    
    div[data-baseweb="select"] {
        font-size: 18px !important;
    }

    [data-testid="stMetricLabel"] p {
        font-size: 20px !important;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def carregar_dados():
    conexao = sqlite3.connect('historico_precos.db')
    df = pd.read_sql('SELECT * FROM historico', conexao)
    conexao.close()
    return df

df = carregar_dados()

col1, col2 = st.columns([2, 1])

with col1:
    modelos_disponiveis = df["Modelo_Padronizado"].unique().tolist()
    modelos_disponiveis.insert(0, "Todos")
    modelo_selecionado = st.selectbox("Escolha o Modelo:", modelos_disponiveis)

with col2:
    preco_maximo = st.slider(
        "Preço Máximo (R$):",
        min_value=int(df['Preco'].min()),
        max_value=int(df['Preco'].max()),
        value=int(df['Preco'].max())
    )
st.divider()


# Aplicando os Filtros no Pandas
df_filtrado = df.copy()

if modelo_selecionado != "Todos":
    df_filtrado = df_filtrado[df_filtrado['Modelo_Padronizado'] == modelo_selecionado]

df_filtrado = df_filtrado[df_filtrado['Preco'] <= preco_maximo]   


# Cartões Indicadores (KPIs)
st.subheader("Resumo do Mercado")

if not df_filtrado.empty:
    # achando a linha com menor preço
    id_menor_preco = df_filtrado['Preco'].idxmin()
    linha_melhor_oferta = df_filtrado.loc[id_menor_preco]

    menor_preco = linha_melhor_oferta['Preco']
    link_melhor_oferta = linha_melhor_oferta['Link']
    nome_bruto = linha_melhor_oferta['Modelo_Original']
    nome_exibicao = nome_bruto[:35] + "..." if len(nome_bruto) > 35 else nome_bruto
    preco_medio = df_filtrado['Preco'].mean()

    kpi1, kpi2, kpi3 = st.columns(3)

    with kpi1:
        # usando replace para transformar do americano (1,500.00) para o BR (1.500,00)
        texto_menor_preco = f"R$ {menor_preco:,.2f}".replace(",","X").replace(".",",").replace("X",".")
        st.metric(label="Melhor Oferta", value=texto_menor_preco)

        st.markdown(f"**[{nome_exibicao}]({link_melhor_oferta})**")

    with kpi2:
        texto_preco_medio = f"R$ {preco_medio:,.2f}".replace(",","X").replace(".",",").replace("X",".")
        st.metric(label="Preço Médio", value=texto_preco_medio)

    with kpi3:
        st.metric(label="Anúncios Ativos", value=len(df_filtrado))
else:
    st.warning("Nenhum anúncio encontrado com esses filtros.")
st.divider()


# Gráfico Histórico de Preços
st.subheader("Histórico da Melhor Oferta")

if not df_filtrado.empty:
    # agrupa os dados por data e pega o menor preço de cada dia
    df_grafico = df_filtrado.groupby('Data_Coleta')['Preco'].min().reset_index()

    # a data será o índice (eixo X)
    df_grafico.set_index('Data_Coleta', inplace=True)

    st.line_chart(df_grafico, y='Preco', height=250)
st.divider()


# Exibindo a Tabela Final
st.subheader(f"Anúncios Encontrados")
df_vitrine = df_filtrado.sort_values(by="Preco", ascending=True)
st.dataframe(
    df_vitrine,
    column_config={
        "Preco": st.column_config.NumberColumn(
            "Preço",
            format="R$ %.2f"
        ),
        "Modelo_Padronizado": "Modelo",
        "Modelo_Original": "Anúncio",
        "Link": st.column_config.LinkColumn(
            "Link de Compra",
            display_text= "Ir para o anúncio"
        ),
        "Data_Coleta": st.column_config.TextColumn(
            "Visto em"
        )
    },
    hide_index=True,
    width='stretch',
    column_order=["Modelo_Padronizado", "Preco", "Link", "Modelo_Original", "Data_Coleta"]
)

st.divider() 
rodape = """
<div style="text-align: center; margin-top: 20px; color: #888;">
    <p>Desenvolvido por <b>Leo Bizzocchi</b></p>
</div>
"""
st.markdown(rodape, unsafe_allow_html=True)
