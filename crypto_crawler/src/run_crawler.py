from crawler.coingecko_spider import CoinGeckoSpider
from crawler.historical_data import get_crypto_historical_data
from datetime import datetime
import json
from pathlib import Path

def check_historical_data_exists(symbol: str) -> bool:
    """Verifica se já existem dados históricos para o símbolo especificado"""
    output_dir = Path("data/historical")
    historical_files = list(output_dir.glob(f"{symbol.lower()}_historical_*.json"))
    return len(historical_files) > 0

def save_historical_data(data, symbol):
    """Save historical data to JSON file"""
    output_dir = Path("data/historical")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Convert DataFrame to dict and format the data
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
    
    filename = output_dir / f"{symbol.lower()}_historical_complete.json"
    with open(filename, 'w') as f:
        json.dump(data_dict, f, indent=4)
    print(f"Historical data saved to {filename}")

def main():
    symbol = 'bitcoin'
    
    # Verifica se já existem dados históricos
    if not check_historical_data_exists(symbol):
        print("Dados históricos não encontrados. Iniciando coleta histórica desde 2014...")
        historical_data = get_crypto_historical_data(
            symbol='BTC-USD',
            interval='1d'
        )
        
        if not historical_data.empty:
            save_historical_data(historical_data, symbol)
        else:
            print("Erro: Não foi possível coletar dados históricos!")
            return
    else:
        print("Dados históricos já existem. Pulando coleta histórica.")
    
    # 2. Start real-time crawler
    print("\nIniciando coleta de dados em tempo real...")
    spider = CoinGeckoSpider()
    spider.run(interval=60)  # Collect data every 60 seconds

if __name__ == "__main__":
    main() 