# 🔗 MVP de Engenharia de Dados - Rastreador de Criptoativos

Este projeto é o MVP (Mínimo Produto Viável) desenvolvido para a disciplina de Engenharia de Dados da pós-graduação em Ciência de Dados e Analitycs.

O objetivo é construir um pipeline completo de coleta, modelagem, carga e análise de dados de criptoativos, utilizando a nuvem AWS e ferramentas open source.

---

## 🚀 Objetivo

O objetivo deste projeto é desenvolver um pipeline de engenharia de dados voltado para o rastreamento e análise de criptoativos. O sistema será responsável por coletar dados históricos de preços de diferentes ativos digitais por meio da API pública da CoinGecko, armazená-los na nuvem (AWS) e estruturá-los de forma que possam ser utilizados em análises futuras.

Inicialmente, o foco estará na construção da infraestrutura de coleta, modelagem, carga e análise de dados. Em etapas futuras, os dados serão reutilizados em projetos de ciência de dados para geração de insights e modelos preditivos voltados à identificação de oportunidades de entrada no mercado.

### 🎯 Problema a ser resolvido

**Como identificar criptoativos com comportamentos que possam indicar oportunidades de investimento, utilizando dados históricos de preços e volume?**

### ❓ Perguntas que o projeto respondeu
Durante a construção do MVP, com os dados organizados e estruturados na arquitetura Lakehouse, foram exploradas as seguintes perguntas de negócio:

Qual o ativo com maior preço médio no período?

Qual o ativo com maior desvio padrão de preço?

Qual ativo apresentou o maior volume médio negociado?

Existe alguma correlação entre volume negociado e preço médio?

Quais as estatísticas básicas dos ativos disponíveis (mínimo, máximo, total de registros, etc)?

⚠️ Observação: Esta etapa focou na exploração inicial dos dados com base nas informações coletadas e tratadas. Análises mais avançadas (como predições, agrupamentos ou padrões comportamentais) poderão ser conduzidas futuramente, em disciplinas voltadas para ciência de dados.

> ⚠️ **Observação:** Este trabalho se concentra na construção da fundação de dados (engenharia), sendo a parte de análises preditivas e identificação automatizada de oportunidades explorada futuramente em disciplinas de ciência de dados.

---

## 🔧 Tecnologias Utilizadas
AWS Lambda – Coleta automatizada diária

AWS S3 – Armazenamento de dados brutos

Databricks – Plataforma principal para processamento de dados, incluindo:

Delta Lake – Armazenamento e versionamento de dados

Autoloader – Ingestão automática de dados

Structured Streaming – Processamento de dados em tempo real

Unity Catalog – Governança e catálogo de dados

Python – requests, pandas, entre outras bibliotecas

CoinGecko API – Fonte dos dados de criptoativos

---

## 🗂️ Estrutura do Projeto

```plaintext
.
├── analise/                # Notebooks e documentos de análise de dados
│   ├── analise_qualidade_dados.md           # Documento descritivo da análise de qualidade dos dados
│   ├── analise_qualidade_silver.ipynb       # Notebook com os códigos utilizados na análise de qualidade
│   └── discussao_resultado.md               # Discussão dos resultados obtidos com base nas perguntas do projeto
├── avaliacao/              # Autoavaliação e materiais relacionados
│   └── autoavaliacao.md                     # Documento de autoavaliação com reflexões sobre o projeto
├── catalogo_de_dados/      # Catálogo de dados com descrição dos campos e domínios
│   ├── catalogo_de_dados_bronze.md          # Descrição da estrutura de dados na camada Bronze
│   └── catalogo_de_dados_silver.md.ipynb    # Notebook com descrição detalhada da camada Silver
├── crypto_data_extractor/  # Código da função Lambda para coleta dos dados
│   ├── lambda_layer                          # Pacote com dependências da Lambda em formato .zip
│   │   └── lambda_dependencies_layer.zip     # Arquivo com bibliotecas utilizadas pela Lambda
│   ├── src                                   # Código-fonte do extrator
│   │   ├── crawler
│   │   │   └── fetcher.py                    # Script principal responsável pela extração de dados via API
│   │   └── __init__.py                       # Inicializador de módulo Python
│   ├── lambda_function_code.zip              # Código empacotado da função Lambda para deploy
│   └── requirements.txt                      # Lista de dependências da aplicação
├── docs/                   # Prints de tela e vídeos com evidências de execução
├── lakehouse/              # Notebooks e scripts relacionados ao Databricks
│   ├── 01.bronze                            # Processamento da camada Bronze
│   │   ├── processaDiario.ipynb             # Processa dados diários dos criptoativos para Delta Bronze
│   │   └── processaHistorico.ipynb          # Processa dados históricos dos criptoativos para Delta Bronze
│   ├── 02.silver                            # Processamento da camada Silver
│   │   └── processamentoDominioCripto.ipynb # Unificação de dados em uma tabela Silver para o domínio de criptoativos
│   └── 03.gold                              # Geração de visões analíticas (Gold)
│       └── visoesDominioCripto.ipynb        # Visões analíticas sobre os ativos para possíveis análises futuras
└── README.md               # Este arquivo com a descrição geral do projeto

```

---

## 📅 Frequência de Coleta

- Diária (via AWS Lambda)
- Endpoints utilizados: `/coins/{id}/market_chart`, entre outros da [CoinGecko API](https://www.coingecko.com/en/api)

---

## 🧪 Como Executar Localmente

1. Clone o repositório:

```bash
git clone https://github.com/douglas-engenheirodedados/mvpEngDadosPosPuc
cd crypto_data_extractor
```

2. Crie um ambiente virtual e instale as dependências:

```bash
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate no Windows
pip install -r requirements.txt
```

3. Execute o script de coleta manualmente (opcional):

```bash
python src/crawler/fetcher #adequar os endpoints da API e S3 para o seu contexto.
```

---

## 🧾 Licença dos Dados

Este projeto utiliza dados públicos disponibilizados pela [CoinGecko API](https://www.coingecko.com/en/api), sob seus termos de uso.

---

## ✅ Checklist para Entrega

✅ Objetivo e perguntas de negócio definidos

✅ Coleta automática implementada

✅ Modelagem e catálogo de dados

✅ Pipeline de dados com Databricks

✅ Análise de dados (qualidade + solução)

✅ Autoavaliação escrita

✅ Evidências (prints e/ou vídeos) adicionadas em docs/

✅ Código hospedado em repositório público do GitHub

---

## ✍️ Autor

- **Nome:** Douglas Littig
- **Curso:** Pós-graduação em Ciência de Dados e Analitycs