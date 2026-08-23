# Radar de Mercado: Pipeline ETL Automatizado de Preços de Baixos Tagima

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2C2D72?style=for-the-badge&logo=pandas&logoColor=white)
![Selenium](https://img.shields.io/badge/Selenium-43B02A?style=for-the-badge&logo=selenium&logoColor=white)
![BeautifulSoup](https://img.shields.io/badge/BeautifulSoup-499C54?style=for-the-badge&logo=python&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)

## O Problema e a Solução
Comprar instrumentos musicais exige pesquisa constante, pois os preços flutuam diariamente e as boas oportunidades desaparecem rápido. Rastrear anúncios manualmente em marketplaces é um processo lento e ineficiente.

Este projeto resolve esse problema através de um **Pipeline de Dados End-to-End**. Ele monitora, extrai, limpa, armazena e visualiza o histórico de preços de contrabaixos Tagima no Mercado Livre. O objetivo é criar uma ferramenta autônoma de inteligência de mercado que destaca as melhores ofertas do dia e mostra as tendências de alta ou queda de preços ao longo do tempo.

**[Acesse o Dashboard Interativo na Nuvem Aqui](https://etl-monitoramento-baixos-leobizzocchi.streamlit.app/)**
<img width="1816" height="657" alt="image" src="https://github.com/user-attachments/assets/5d2a7efb-0ccc-4749-becc-bc9333d1e543" />

## Arquitetura e Fluxo de Dados (ETL)

O sistema opera de forma 100% automatizada e assíncrona, dividido nas seguintes etapas:

*   **Extract (Extração):** O `Selenium` assume o controle de um navegador invisível, driblando sistemas anti-bot (usando camuflagem de User-Agent), rola a página e carrega o código-fonte. Em seguida, o `BeautifulSoup` entra em ação para analisar o HTML (parsing) e extrair cirurgicamente as tags contendo títulos, links e preços.
*   **Transform (Transformação):** Com os dados brutos em mãos, o Pandas aplica regras de negócio: remove caracteres especiais de moedas e converte textos para números flutuantes. Para categorizar com precisão cada anúncio no seu modelo específico de baixo, o algoritmo combina expressões regulares com Fuzzy Matching (cálculo de Distância de Levenshtein). Isso garante o agrupamento correto dos produtos e a consistência da análise, mesmo lidando com variações de nomenclatura e erros de digitação frequentes nos títulos originais.
*   **Load (Carregamento):** O dataset consolidado é injetado em um banco de dados relacional `SQLite`, gerando um registro histórico contínuo (séries temporais) que previne a perda de dados entre execuções.
*   **Automação (Scheduling):** Um script Batch (`.bat`) integrado ao Agendador de Tarefas do Windows liga o robô diariamente em horário agendado. Após a coleta, o script executa comandos Git automaticamente para fazer o push do banco atualizado para a nuvem.
*   **Visualização:** O front-end foi construído com `Streamlit`. Ele consome o SQLite da nuvem e gera uma interface responsiva contendo KPIs (Melhor Oferta, Preço Médio), filtros dinâmicos reativos e gráficos interativos para apoiar a decisão de compra.

## Tecnologias Utilizadas
*   **Linguagem Core:** Python 3
*   **Coleta e Parsing:** Selenium WebDriver, WebDriver Manager, BeautifulSoup4 (BS4)
*   **Engenharia de Dados:** Pandas
*   **Armazenamento:** SQLite3
*   **Front-end e Deploy:** Streamlit, Streamlit Community Cloud
*   **DevOps e Versionamento:** Git, GitHub, Windows Task Scheduler, Batch Scripting (.bat)
