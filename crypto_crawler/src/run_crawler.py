from crawler.coingecko_spider import CoinGeckoSpider
from crawler.historical_data import get_crypto_historical_data
from datetime import datetime
import json
from pathlib import Path

def check_historical_data_exists(symbol: str) -> bool:
    """
    Verifica se já existem dados históricos para a criptomoeda especificada.
    
    Args:
        symbol: Nome da criptomoeda (ex: 'bitcoin')
    
    Returns:
        bool: True se existirem arquivos históricos, False caso contrário
    """
    output_dir = Path("data/historical")
    historical_files = list(output_dir.glob(f"{symbol.lower()}_historical_*.json"))
    return len(historical_files) > 0

def save_historical_data(data, symbol):
    """
    Salva dados históricos em arquivo JSON com metadados.
    
    Args:
        data: DataFrame com dados históricos
        symbol: Nome da criptomoeda
    """
    # Cria diretório se não existir
    output_dir = Path("data/historical")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Prepara dicionário com metadados e dados
    data_dict = {
        'metadata': {
            'coin': symbol,
            'source': 'Yahoo Finance',
            'start_date': data.index[0].strftime('%Y-%m-%d'),
            'end_date': data.index[-1].strftime('%Y-%m-%d'),
            'data_points': len(data),
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        'data': []
    }
    
    # Converte cada linha do DataFrame para o formato JSON
    for date, row in data.iterrows():
        data_dict['data'].append({
            'date': date.strftime('%Y-%m-%d'),
            'open': row['Open'],
            'high': row['High'],
            'low': row['Low'],
            'close': row['Close'],
            'volume': row['Volume'],
            'source': row['source']
        })
    
    # Salva arquivo JSON completo
    filename = output_dir / f"{symbol.lower()}_historical_complete.json"
    with open(filename, 'w') as f:
        json.dump(data_dict, f, indent=4)
    print(f"Historical data saved to {filename}")

def main():
    """
    Função principal que orquestra o fluxo de coleta de dados.
    Gerencia tanto a coleta histórica quanto em tempo real.
    """
    symbol = 'bitcoin'
    
    # Verifica necessidade de coleta histórica
    if not check_historical_data_exists(symbol):
        print("Dados históricos não encontrados. Iniciando coleta histórica desde 2014...")
        historical_data = get_crypto_historical_data(
            symbol='BTC-USD',
            interval='1d'
        )
        
        # Salva dados históricos se coletados com sucesso
        if not historical_data.empty:
            save_historical_data(historical_data, symbol)
        else:
            print("Erro: Não foi possível coletar dados históricos!")
            return
    else:
        print("Dados históricos já existem. Pulando coleta histórica.")
    
    # Inicia coleta em tempo real
    print("\nIniciando coleta de dados em tempo real...")
    spider = CoinGeckoSpider()
    spider.run(interval=60)  # Coleta a cada 60 segundos

if __name__ == "__main__":
    main() 