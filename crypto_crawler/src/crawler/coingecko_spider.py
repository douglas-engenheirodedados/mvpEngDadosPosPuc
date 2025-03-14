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
    """
    Spider para coletar dados em tempo real do Bitcoin via API CoinGecko.
    Gerencia tanto a coleta quanto o armazenamento dos dados.
    """
    
    def __init__(self):
        # URL base da API CoinGecko
        self.base_url = "https://api.coingecko.com/api/v3"
        
        # Headers padrão para requisições
        self.headers = {
            'Accept': 'application/json'
        }
        
        # Obtém e valida a chave da API do arquivo .env
        self.api_key = os.getenv('COINGECKO_API_KEY')
        if not self.api_key:
            raise ValueError("API key não encontrada. Verifique seu arquivo .env")
            
        # Define e cria diretórios para armazenamento
        self.output_dir = Path("data/historical")  # Dados históricos
        self.realtime_dir = Path("data/realtime")  # Dados em tempo real
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.realtime_dir.mkdir(parents=True, exist_ok=True)

    def check_historical_data(self) -> bool:
        """
        Verifica se existem dados históricos na pasta.
        
        Returns:
            bool: True se existirem arquivos históricos, False caso contrário
        """
        files = list(self.output_dir.glob('bitcoin_historical_*.json'))
        return len(files) > 0

    def get_latest_data_date(self) -> datetime:
        """
        Obtém a data mais recente dos dados históricos.
        Percorre todos os arquivos históricos para encontrar o registro mais recente.
        
        Returns:
            datetime: Data do último registro encontrado
        """
        files = list(self.output_dir.glob('bitcoin_historical_*.json'))
        latest_date = datetime(2013, 1, 1)  # Data inicial padrão
        
        for file in files:
            with open(file, 'r') as f:
                data = json.load(f)
                if data['data']:
                    last_entry = data['data'][-1]
                    date = datetime.strptime(last_entry['date'], '%Y-%m-%d')
                    if date > latest_date:
                        latest_date = date
        return latest_date

    def fetch_realtime_data(self) -> Optional[Dict]:
        """
        Busca dados em tempo real do Bitcoin via API CoinGecko.
        Inclui tratamento de rate limit e erros de requisição.
        
        Returns:
            Dict | None: Dados do Bitcoin ou None em caso de erro
        """
        endpoint = f"{self.base_url}/simple/price"
        params = {
            'ids': 'bitcoin',
            'vs_currencies': 'usd',
            'include_market_cap': 'true',
            'include_24hr_vol': 'true',
            'include_24hr_change': 'true',
            'include_last_updated_at': 'true'
        }
        headers = {
            'X-CG-Pro-API-Key': self.api_key
        }

        try:
            response = requests.get(endpoint, params=params, headers=headers)
            # Tratamento de rate limit
            if response.status_code == 429:
                print("Rate limit atingido. Aguardando 60 segundos...")
                time.sleep(60)
                return self.fetch_realtime_data()  # Tenta novamente após espera
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Erro ao buscar dados: {e}")
            return None

    def save_realtime_data(self, data: Dict) -> None:
        """
        Salva os dados em tempo real em arquivos JSON individuais.
        Organiza os arquivos em estrutura hierárquica por ano/mês/dia.
        
        Args:
            data: Dicionário com dados do Bitcoin
        """
        if not data:
            return

        # Captura o momento exato da coleta
        timestamp = datetime.now()
        
        # Formata os dados com metadados
        formatted_data = {
            'metadata': {
                'coin': 'bitcoin',
                'source': 'CoinGecko API',
                'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'created_at': timestamp.strftime('%Y-%m-%d %H:%M:%S')
            },
            'data': {
                'price': data['bitcoin']['usd'],
                'market_cap': data['bitcoin'].get('usd_market_cap'),
                'volume': data['bitcoin'].get('usd_24h_vol'),
                'change_24h': data['bitcoin'].get('usd_24h_change'),
                'source': 'coingecko'
            }
        }

        # Cria estrutura de diretórios hierárquica
        year_dir = self.realtime_dir / timestamp.strftime('%Y')
        month_dir = year_dir / timestamp.strftime('%m')
        day_dir = month_dir / timestamp.strftime('%d')
        day_dir.mkdir(parents=True, exist_ok=True)

        # Gera nome do arquivo com timestamp completo
        filename = day_dir / f"bitcoin_realtime_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"

        try:
            # Salva dados formatados em JSON
            with open(filename, 'w') as f:
                json.dump(formatted_data, f, indent=4)
            print(f"Dados salvos em: {filename}")
        except Exception as e:
            print(f"Erro ao salvar dados: {e}")

    def run(self, interval: int = 60) -> None:
        """
        Executa o crawler em loop contínuo.
        Coleta e salva dados em intervalos regulares.
        
        Args:
            interval: Intervalo entre coletas em segundos (default: 60)
        """
        print("Iniciando coleta de dados em tempo real...")
        
        # Verifica pré-requisitos
        if not self.check_historical_data():
            print("Dados históricos não encontrados. Por favor, execute primeiro o YahooFinanceSpider.")
            return

        # Verifica status dos dados históricos
        latest_date = self.get_latest_data_date()
        if latest_date.date() >= datetime.now().date():
            print("Dados históricos já estão atualizados. Iniciando coleta em tempo real...")
        else:
            print(f"Dados históricos disponíveis até {latest_date.date()}. Iniciando coleta em tempo real...")

        try:
            # Loop principal de coleta
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