import os
from dotenv import load_dotenv
import requests
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

class CoinGeckoSpider:
    """Spider para coletar dados em tempo real de criptomoedas via API CoinGecko."""
    
    # Dicionário de configuração das criptomoedas
    CRYPTO_CONFIG = {
        'bitcoin': {
            'symbol': 'BTC-USD',
            'coingecko_id': 'bitcoin'
        },
        'ethereum': {
            'symbol': 'ETH-USD',
            'coingecko_id': 'ethereum'
        }
    }
    
    def __init__(self, cryptocurrencies: List[str] = None):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.headers = {
            'Accept': 'application/json'
        }
        
        # Lista de criptomoedas para monitorar
        self.cryptocurrencies = cryptocurrencies or ['bitcoin', 'ethereum']
        
        # Validar criptomoedas
        for crypto in self.cryptocurrencies:
            if crypto not in self.CRYPTO_CONFIG:
                raise ValueError(f"Criptomoeda não suportada: {crypto}")
        
        self.api_key = os.getenv('COINGECKO_API_KEY')
        if not self.api_key:
            raise ValueError("API key não encontrada. Verifique seu arquivo .env")
            
        # Criar estrutura de diretórios para cada criptomoeda
        self.base_dir = Path("data")
        for crypto in self.cryptocurrencies:
            (self.base_dir / crypto / "historical").mkdir(parents=True, exist_ok=True)
            (self.base_dir / crypto / "realtime").mkdir(parents=True, exist_ok=True)

    def check_historical_data(self, crypto: str) -> bool:
        """Verifica se existem dados históricos para uma criptomoeda específica."""
        files = list((self.base_dir / crypto / "historical").glob(f'{crypto}_historical_*.json'))
        return len(files) > 0

    def get_latest_data_date(self, crypto: str) -> datetime:
        """Obtém a data mais recente dos dados históricos para uma criptomoeda."""
        files = list((self.base_dir / crypto / "historical").glob(f'{crypto}_historical_*.json'))
        latest_date = datetime(2013, 1, 1)
        
        for file in files:
            with open(file, 'r') as f:
                data = json.load(f)
                if data['data']:
                    last_entry = data['data'][-1]
                    date = datetime.strptime(last_entry['date'], '%Y-%m-%d')
                    if date > latest_date:
                        latest_date = date
        return latest_date

    def fetch_realtime_data(self) -> Dict:
        """Busca dados em tempo real para todas as criptomoedas configuradas."""
        endpoint = f"{self.base_url}/simple/price"
        ids = ','.join(self.CRYPTO_CONFIG[crypto]['coingecko_id'] for crypto in self.cryptocurrencies)
        
        params = {
            'ids': ids,
            'vs_currencies': 'usd',
            'include_market_cap': 'true',
            'include_24hr_vol': 'true',
            'include_24hr_change': 'true',
            'include_last_updated_at': 'true'
        }
        headers = {'X-CG-Pro-API-Key': self.api_key}

        try:
            response = requests.get(endpoint, params=params, headers=headers)
            if response.status_code == 429:
                print("Rate limit atingido. Aguardando 60 segundos...")
                time.sleep(60)
                return self.fetch_realtime_data()
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Erro ao buscar dados: {e}")
            return {}

    def save_realtime_data(self, data: Dict) -> None:
        """Salva dados em tempo real para cada criptomoeda."""
        if not data:
            return

        timestamp = datetime.now()
        
        for crypto in self.cryptocurrencies:
            if self.CRYPTO_CONFIG[crypto]['coingecko_id'] not in data:
                continue

            crypto_data = data[self.CRYPTO_CONFIG[crypto]['coingecko_id']]
            
            formatted_data = {
                'metadata': {
                    'coin': crypto,
                    'source': 'CoinGecko API',
                    'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    'created_at': timestamp.strftime('%Y-%m-%d %H:%M:%S')
                },
                'data': {
                    'price': crypto_data['usd'],
                    'market_cap': crypto_data.get('usd_market_cap'),
                    'volume': crypto_data.get('usd_24h_vol'),
                    'change_24h': crypto_data.get('usd_24h_change'),
                    'source': 'coingecko'
                }
            }

            # Criar estrutura de diretórios para a criptomoeda específica
            year_dir = self.base_dir / crypto / "realtime" / timestamp.strftime('%Y')
            month_dir = year_dir / timestamp.strftime('%m')
            day_dir = month_dir / timestamp.strftime('%d')
            day_dir.mkdir(parents=True, exist_ok=True)

            filename = day_dir / f"{crypto}_realtime_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"

            try:
                with open(filename, 'w') as f:
                    json.dump(formatted_data, f, indent=4)
                print(f"Dados de {crypto} salvos em: {filename}")
            except Exception as e:
                print(f"Erro ao salvar dados de {crypto}: {e}")

    def run(self, interval: int = 60) -> None:
        """Executa o crawler para todas as criptomoedas configuradas."""
        print("Iniciando coleta de dados em tempo real...")
        
        # Verificar dados históricos para cada criptomoeda
        for crypto in self.cryptocurrencies:
            if not self.check_historical_data(crypto):
                print(f"Dados históricos não encontrados para {crypto}.")
                continue

            latest_date = self.get_latest_data_date(crypto)
            print(f"Dados históricos de {crypto} disponíveis até {latest_date.date()}")

        try:
            while True:
                data = self.fetch_realtime_data()
                self.save_realtime_data(data)
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\nColeta interrompida pelo usuário.")

    def get_current_price(self, coins: List[str], vs_currencies: List[str]) -> Dict:
        """
        Get current price for multiple cryptocurrencies
        
        Args:
            coins: List of coin ids (e.g., ['bitcoin', 'ethereum'])
            vs_currencies: List of currencies (e.g., ['usd', 'eur'])
        """
        endpoint = f"{self.base_url}/simple/price"
        params = {
            'ids': ','.join(coins),
            'vs_currencies': ','.join(vs_currencies)
        }
        
        try:
            response = requests.get(endpoint, params=params, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching prices: {e}")
            return {}

    def get_coin_market_data(self, coin_id: str) -> Dict:
        """
        Get detailed market data for a specific coin
        
        Args:
            coin_id: Coin identifier (e.g., 'bitcoin')
        """
        endpoint = f"{self.base_url}/coins/{coin_id}"
        params = {
            'localization': False,
            'tickers': True,
            'market_data': True,
            'community_data': False,
            'developer_data': False
        }
        
        try:
            response = requests.get(endpoint, params=params, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching market data: {e}")
            return {}