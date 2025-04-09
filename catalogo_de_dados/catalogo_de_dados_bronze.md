# 📚 Catálogo de Dados - Camada Bronze

## 📁 Tabela: `bronze.historico_cripto`

### 📄 Descrição:
Tabela contendo o histórico de preços diários de criptoativos, coletados via Yahoo Finance.

### 🧩 Schema:
| Coluna          | Tipo        | Descrição                              | Domínio / Valores Esperados                |
|-----------------|-------------|----------------------------------------|--------------------------------------------|
| asset_name      | string      | Nome do ativo                          | Ex: "bitcoin", "ethereum"                  |
| ticker          | string      | Ticker do ativo conforme Yahoo Finance | Ex: "BTC-USD"                              |
| extraction_date | timestamp   | Data e hora da coleta dos dados        | Data/hora da execução do pipeline          |
| source          | string      | Fonte original dos dados               | "Yahoo Finance"                            |
| timestamp       | timestamp   | Data da cotação histórica              | 2010-01-01 até atual                       |
| price_usd       | double      | Preço em dólares na data indicada      | Valor ≥ 0                                  |
| source_file     | string      | Nome do arquivo origem                 | Nome do json                               |

---

## 📁 Tabela: `bronze.intradiario_cripto`

### 📄 Descrição:
Tabela contendo os preços intradiários (de hora em hora) de criptoativos, coletados via CoinGecko.

### 🧩 Schema:
| Coluna          | Tipo       | Descrição                                         | Domínio / Valores Esperados                |
|-----------------|------------|---------------------------------------------------|--------------------------------------------|
| asset_name      | string     | Nome do ativo                                     | Ex: "bitcoin", "ethereum"                  |
| timestamp       | timestamp  | Horário da cotação                                | Ex: "2025-04-06 01:04:52"                  |
| price_usd       | double     | Preço em dólares no horário indicado              | Valor ≥ 0                                  |
| extraction_date | timestamp  | Data e hora da coleta dos dados                   | Data/hora da execução do pipeline          |
| source          | string     | Fonte original dos dados                          | "CoinGecko"                                |
| time_interval   | string     | Intervalo de tempo coberto no arquivo intradiário | "YYYY-MM-DD HH:mm:ss to HH:mm:ss"          |
| source_file     | string     | Nome do arquivo origem                            | Nome do json                               |

---

## 🔗 Linhagem de Dados

### Origem:
- `bronze_historico` → Arquivos JSON de histórico em `landing/historico/{ativo}.json`

- `bronze_intradiario` → Arquivos JSON diários em `landing/cripto/{ativo}/YYYY-MM-DD.json`

### Transformação:
- Explosão do campo `data` para linhas
- Inclusão dos metadados como colunas adicionais
- Conversão dos arquivos JSON para Delta formatado

## 🛠️ Detalhes Técnicos e Estratégia de Ingestão

### 🔄 Evolução de Schema
A ingestão de arquivos JSON via Autoloader utiliza inferência automática de schema (`cloudFiles.inferColumnTypes = true`). Com isso:

- O sistema detecta dinamicamente novas colunas nos arquivos da camada landing.
- A estrutura do Delta Table é atualizada conforme necessário, respeitando o controle de schema do Unity Catalog.
- A auditoria de alterações pode ser monitorada por meio da interface do Unity Catalog ou jobs automatizados de verificação.

### 🧪 Regras de Qualidade de Dados (planejadas)
Serão implementadas validações automáticas para garantir integridade mínima dos dados antes da persistência na bronze:

| Coluna         | Validação                               |
|----------------|------------------------------------------|
| `price_usd`    | Deve ser maior ou igual a zero           |
| `timestamp`    | Deve ter formato válido (`timestamp`)    |
| `asset_name`   | Não pode ser nulo                        |
| `source`       | Não pode ser nulo                        |

Essas regras poderão ser integradas com [Delta Expectations](https://docs.databricks.com/en/delta-live-tables/expectations.html) futuramente.

### 🔍 Auditabilidade e Linhagem
O uso do **Unity Catalog** permite:

- Rastreabilidade completa da linhagem entre arquivos na `landing`, tabelas `bronze` e futuras camadas `silver` e `gold`.
- Visualização da linhagem e do histórico de alterações na interface gráfica do Databricks.
- Controle de acesso centralizado por workspace, catalog e schema.

### ⚙️ Formato e Performance
- Todas as tabelas são salvas em formato **Delta Lake**, permitindo funcionalidades como *Time Travel*, *Vacuum* e *Optimize*.
- O processamento está sendo realizado com clusters **Photon-enabled (Liquid Clusters)**, otimizando leitura e escrita de arquivos de médio porte (< 1 TB).

