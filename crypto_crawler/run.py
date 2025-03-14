"""Módulo principal para execução do crawler de dados de criptomoedas.
Este módulo integra a coleta de dados históricos do Bitcoin via Yahoo Finance
com a coleta em tempo real via CoinGecko API.

Uso:
    python run.py

Fluxo:
1. Verifica se existem dados históricos
2. Se não existirem, coleta dados históricos via Yahoo Finance
3. Inicia coleta em tempo real via CoinGecko
"""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from src.crawler.yahoo_finance_spider import YahooFinanceSpider
from src.crawler.coingecko_spider import CoinGeckoRealTimeSpider

def main():
    """Função principal que orquestra a coleta de dados históricos e em tempo real.
    
    Primeiro verifica se existem dados históricos. Se não existirem,
    realiza a coleta histórica via Yahoo Finance antes de iniciar
    a coleta em tempo real via CoinGecko.
    """
    # Verifica e atualiza dados históricos primeiro
    yahoo_spider = YahooFinanceSpider()
    coingecko_spider = CoinGeckoRealTimeSpider()

    if not coingecko_spider.check_historical_data():
        print("Baixando dados históricos...")
        yahoo_spider.collect_multiple_years(start_year=2014, end_year=2024)
    
    # Inicia coleta em tempo real
    print("Iniciando coleta em tempo real...")
    coingecko_spider.run()

if __name__ == "__main__":
    main()