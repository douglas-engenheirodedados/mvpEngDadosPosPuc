# Documentação Técnica - Crypto Crawler

## Visão Geral do Sistema

O sistema é composto por dois coletores principais:
1. Coletor de dados históricos (Yahoo Finance)
2. Coletor de dados em tempo real (CoinGecko)

## Estrutura do Código

### 1. Historical Data Module (`historical_data.py`)

```python
def get_crypto_historical_data(symbol: str, start_date: Optional[datetime] = None, 
                             end_date: Optional[datetime] = None, interval: str = "1d") -> pd.DataFrame
```

**Funcionalidade**: Coleta dados históricos do Yahoo Finance
- **Parâmetros**:
  - `symbol`: Símbolo da criptomoeda (ex: 'BTC-USD')
  - `start_date`: Data inicial (default: 01/01/2014)
  - `end_date`: Data final (default: data atual)
  - `interval`: Intervalo dos dados (default: '1d')
- **Retorno**: DataFrame com dados históricos
- **Campos retornados**: Open, High, Low, Close, Volume, source

### 2. CoinGecko Spider (`coingecko_spider.py`)

#### Classe `CoinGeckoSpider`

**Atributos**:
```python
self.base_url: str  # URL base da API
self.headers: Dict  # Headers da requisição
self.api_key: str   # Chave da API do CoinGecko
self.output_dir: Path  # Diretório para dados históricos
self.realtime_dir: Path  # Diretório para dados em tempo real
```

**Métodos Principais**:

1. `check_historical_data(self) -> bool`
   - Verifica existência de dados históricos
   - Retorna: True se existirem dados históricos

2. `get_latest_data_date(self) -> datetime`
   - Obtém a data mais recente dos dados históricos
   - Retorna: Data do último registro histórico

3. `fetch_realtime_data(self) -> Dict`
   - Coleta dados em tempo real da API
   - Tratamento de rate limits
   - Retorna: Dados atuais do Bitcoin

4. `save_realtime_data(self, data: Dict)`
   - Salva dados em tempo real
   - Estrutura hierárquica: ano/mês/dia
   - Nome do arquivo: `bitcoin_realtime_YYYYMMDD_HHMMSS.json`

5. `run(self, interval: int = 60)`
   - Executa o crawler em loop
   - Intervalo padrão: 60 segundos
   - Tratamento de interrupção do usuário

### 3. Run Crawler (`run_crawler.py`)

**Funções Principais**:

1. `check_historical_data_exists(symbol: str) -> bool`
   - Verifica existência de arquivo histórico
   - Parâmetro: symbol (nome da moeda)

2. `save_historical_data(data: pd.DataFrame, symbol: str)`
   - Converte DataFrame para JSON
   - Adiciona metadados
   - Salva em arquivo único

3. `main()`
   - Orquestra o fluxo de execução
   - Verifica/coleta dados históricos
   - Inicia coleta em tempo real

## Estrutura de Dados

### Dados Históricos (JSON)
```json
{
    "metadata": {
        "coin": str,
        "source": str,
        "start_date": str,
        "end_date": str,
        "data_points": int,
        "created_at": str
    },
    "data": [
        {
            "date": str,
            "open": float,
            "high": float,
            "low": float,
            "close": float,
            "volume": float,
            "source": str
        }
    ]
}
```

### Dados em Tempo Real (JSON)
```json
{
    "metadata": {
        "coin": str,
        "source": str,
        "timestamp": str,
        "created_at": str
    },
    "data": {
        "price": float,
        "market_cap": float,
        "volume": float,
        "change_24h": float,
        "source": str
    }
}
```

## Tratamento de Erros

1. **Historical Data**:
   - Exceções na coleta do Yahoo Finance
   - Retorno de DataFrame vazio em caso de erro

2. **CoinGecko Spider**:
   - Rate limit (429): espera 60 segundos
   - Erros de requisição: log e continuação
   - Erros de salvamento: log do erro

## Configuração

### Variáveis de Ambiente (.env)
```env
COINGECKO_API_KEY=chave_api
```

### Dependências
```
requests
yfinance
pandas
python-dotenv
```

## Boas Práticas Implementadas

1. **Código**:
   - Type hints
   - Docstrings
   - Tratamento de exceções
   - Logging de erros

2. **Dados**:
   - Metadados completos
   - Rastreabilidade (source)
   - Timestamps precisos
   - Estrutura hierárquica

3. **Sistema**:
   - Verificação de dados existentes
   - Tratamento de rate limits
   - Organização modular
   - Configuração via .env

## Limitações Conhecidas

1. **API CoinGecko**:
   - Limites de requisição
   - Possível instabilidade

2. **Dados**:
   - Foco apenas em Bitcoin
   - Armazenamento em JSON
   - Sem validação de dados

3. **Sistema**:
   - Sem recuperação automática
   - Sem compressão de dados
   - Sem backup automático 