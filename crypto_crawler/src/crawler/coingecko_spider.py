import os
from dotenv import load_dotenv
import requests
import json
import time
from datetime import datetime
from pathlib import Path

load_dotenv()

class CoinGeckoRealTimeSpider:
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.api_key = os.getenv('COINGECKO_API_KEY')
        if not self.api_key:
            raise ValueError("API key não encontrada. Verifique seu arquivo .env")
        self.output_dir = Path("data/historical")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def check_historical_data(self):
        """Verifica se existem dados históricos na pasta"""
        files = list(self.output_dir.glob('bitcoin_historical_*.json'))
        return len(files) > 0

    def get_latest_data_date(self):
        """Obtém a data mais recente dos dados históricos"""
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

    def fetch_realtime_data(self):
        """Busca dados em tempo real do Bitcoin"""
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
            if response.status_code == 429:
                print("Rate limit atingido. Aguardando 60 segundos...")
                time.sleep(60)
                return self.fetch_realtime_data()
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Erro ao buscar dados: {e}")
            return None

    def save_realtime_data(self, data):
        """Salva os dados em tempo real"""
        if not data:
            return

        timestamp = datetime.now()
        formatted_data = {
            'date': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'price': data['bitcoin']['usd'],
            'market_cap': data['bitcoin'].get('usd_market_cap'),
            'volume': data['bitcoin'].get('usd_24h_vol'),
            'change_24h': data['bitcoin'].get('usd_24h_change')
        }

        # Cria arquivo do mês atual se não existir
        current_month = timestamp.strftime('%Y_%m')
        filename = self.output_dir / f"bitcoin_realtime_{current_month}.json"

        try:
            if filename.exists():
                with open(filename, 'r') as f:
                    file_data = json.load(f)
            else:
                file_data = {
                    'metadata': {
                        'coin': 'bitcoin',
                        'source': 'CoinGecko API',
                        'month': current_month
                    },
                    'data': []
                }

            file_data['data'].append(formatted_data)
            
            with open(filename, 'w') as f:
                json.dump(file_data, f, indent=4)
                
            print(f"Dados salvos em: {filename}")

        except Exception as e:
            print(f"Erro ao salvar dados: {e}")

    def run(self, interval=60):
        """Executa o crawler em tempo real"""
        print("Iniciando coleta de dados em tempo real...")
        
        if not self.check_historical_data():
            print("Dados históricos não encontrados. Por favor, execute primeiro o YahooFinanceSpider.")
            return

        latest_date = self.get_latest_data_date()
        if latest_date.date() >= datetime.now().date():
            print("Dados históricos já estão atualizados. Iniciando coleta em tempo real...")
        else:
            print(f"Dados históricos disponíveis até {latest_date.date()}. Iniciando coleta em tempo real...")

        try:
            while True:
                data = self.fetch_realtime_data()
                self.save_realtime_data(data)
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\nColeta interrompida pelo usuário.")