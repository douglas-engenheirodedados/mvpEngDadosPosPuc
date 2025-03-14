# MVP Engenharia de Dados - PUC-RJ

Projeto MVP de Engenharia de Dados para o curso de Pós-Graduação em Ciência de Dados e Advanced Analytics da PUC-RJ.

## Sobre o Projeto

Este projeto implementa um sistema de coleta de dados de criptomoedas que combina dados históricos do Yahoo Finance com dados em tempo real da API CoinGecko. O sistema é projetado para criar uma base de dados robusta para análise do mercado de criptomoedas, especialmente Bitcoin.

## Arquitetura do Sistema

### Componentes Principais

1. **Coletor de Dados Históricos**
   - Fonte: Yahoo Finance
   - Período: Desde 2014 até o presente
   - Granularidade: Dados diários
   - Métricas: Preço (abertura, fechamento, máxima, mínima) e volume

2. **Coletor em Tempo Real**
   - Fonte: CoinGecko API
   - Intervalo: 60 segundos
   - Métricas: Preço atual, capitalização de mercado, volume 24h, variação 24h

## Requisitos

- Python 3.8+
- Chave de API do CoinGecko
- Pacotes Python:
  - requests
  - yfinance
  - pandas
  - python-dotenv

## Configuração

1. Clone o repositório:

```bash
git clone https://github.com/seu-usuario/mvpEngDadosPosPuc.git
cd mvpEngDadosPosPuc
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Configure o arquivo `.env`:
```env
COINGECKO_API_KEY=sua_chave_api_aqui
```

## Uso

Execute o coletor:
```bash
python src/run_crawler.py
```

O sistema irá:
1. Verificar a existência de dados históricos
2. Coletar dados históricos se necessário (desde 2014)
3. Iniciar a coleta em tempo real

## Formato dos Dados

### Dados Históricos
```json
{
    "metadata": {
        "coin": "bitcoin",
        "source": "Yahoo Finance",
        "start_date": "2014-01-01",
        "end_date": "2024-03-14",
        "data_points": 3724,
        "created_at": "2024-03-14 10:00:00"
    },
    "data": [
        {
            "date": "2014-01-01",
            "open": 757.5,
            "high": 760.32,
            "low": 750.0,
            "close": 758.12,
            "volume": 12500000,
            "source": "yahoo_finance"
        }
    ]
}
```

### Dados em Tempo Real
```json
{
    "metadata": {
        "coin": "bitcoin",
        "source": "CoinGecko API",
        "timestamp": "2024-03-14 10:00:00",
        "created_at": "2024-03-14 10:00:00"
    },
    "data": {
        "price": 67000.0,
        "market_cap": 1320000000000,
        "volume": 25000000000,
        "change_24h": 2.5,
        "source": "coingecko"
    }
}
```

## Características

- **Rastreabilidade**: Todos os dados incluem fonte e metadados
- **Organização**: Estrutura hierárquica por data para dados em tempo real
- **Resiliência**: Tratamento de erros e limites de API
- **Consistência**: Formato padronizado para dados históricos e em tempo real

## Limitações e Considerações

- A API do CoinGecko possui limites de requisição
- Dados históricos são coletados uma única vez
- O sistema foca exclusivamente no Bitcoin
- Armazenamento em arquivos JSON (pode ser expandido para banco de dados)

## Próximos Passos

- [ ] Implementar suporte a múltiplas criptomoedas
- [ ] Adicionar sistema de banco de dados
- [ ] Implementar pipeline de processamento de dados
- [ ] Criar dashboard de monitoramento
- [ ] Adicionar testes automatizados

## Estrutura do Projeto

```
mvpEngDadosPosPuc/
├── data/
│   ├── historical/
│   └── realtime/
├── src/
│   ├── crawler/
│   │   ├── __init__.py
│   │   ├── coingecko_spider.py
│   │   └── historical_data.py
│   └── run_crawler.py
├── .env
├── .gitignore
├── README.md
└── requirements.txt
```

## Autor

Douglas Littig

## Licença

Este projeto está sob a licença MIT.
