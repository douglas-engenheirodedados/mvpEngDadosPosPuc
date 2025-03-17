import yfinance as yf
from datetime import datetime
import os
import time
import json
from typing import Dict, List
import boto3
from botocore.exceptions import ClientError
import pandas as pd
import requests

class CryptoCrawler:
    def __init__(self):
        # Definindo caminhos dos diretórios
        self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.data_dir = os.path.join(self.base_dir, 'data')
        self.historical_dir = os.path.join(self.data_dir, 'historical')
        self.realtime_dir = os.path.join(self.data_dir, 'realtime')

        # Criando diretórios se não existirem
        for directory in [self.data_dir, self.historical_dir, self.realtime_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)

        self.crypto_list = [
            'BTC-USD',
            'ETH-USD',
            'USDT-USD',
            'BNB-USD'
        ]
        
        # Mapeamento para IDs da CoinGecko
        self.coingecko_ids = {
            'BTC-USD': 'bitcoin',
            'ETH-USD': 'ethereum',
            'USDT-USD': 'tether',
            'BNB-USD': 'binancecoin'
        }
        
        # Inicializa o objeto Tickers uma única vez para dados históricos
        self.tickers = yf.Tickers(' '.join(self.crypto_list))
        
        # Configuração do S3
        self.s3_client = boto3.client('s3')
        self.bucket_name = 'mvppucrj'
        self.base_prefix = '01.landing'

    def _convert_to_dict(self, df, crypto: str) -> List[Dict]:
        """Converte DataFrame para lista de dicionários"""
        data = []
        for date, row in df.iterrows():
            data.append({
                'timestamp': date.strftime('%Y-%m-%d %H:%M:%S'),
                'open': float(row['Open'].iloc[0]) if isinstance(row['Open'], pd.Series) else float(row['Open']),
                'high': float(row['High'].iloc[0]) if isinstance(row['High'], pd.Series) else float(row['High']),
                'low': float(row['Low'].iloc[0]) if isinstance(row['Low'], pd.Series) else float(row['Low']),
                'close': float(row['Close'].iloc[0]) if isinstance(row['Close'], pd.Series) else float(row['Close']),
                'volume': float(row['Volume'].iloc[0]) if isinstance(row['Volume'], pd.Series) else float(row['Volume']),
                'symbol': crypto
            })
        return data

    def _save_to_s3(self, data: Dict, file_path: str) -> None:
        """Salva dados no S3"""
        try:
            s3_key = f"{self.base_prefix}/{file_path}"
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=json.dumps(data, indent=4)
            )
            print(f"Dados salvos com sucesso em s3://{self.bucket_name}/{s3_key}")
        except ClientError as e:
            print(f"Erro ao salvar no S3: {e}")
            raise

    def download_historical_data(self) -> None:
        """Baixa dados históricos de todas as criptomoedas em uma única requisição"""
        print("Verificando e baixando dados históricos...")
        
        try:
            # Obtém dados históricos de todas as criptomoedas em uma única chamada
            historical_data = self.tickers.history(period="max")
            
            for crypto in self.crypto_list:
                # Verifica se já existe arquivo histórico no S3
                s3_path = f"historical/{crypto}_historical.json"
                try:
                    self.s3_client.head_object(Bucket=self.bucket_name, Key=f"{self.base_prefix}/{s3_path}")
                    print(f"Dados históricos de {crypto} já existem no S3")
                except ClientError:
                    # Se não existe, baixa e salva
                    crypto_data = self._convert_to_dict(
                        historical_data.loc[:, historical_data.columns.get_level_values(1)==crypto], 
                        crypto
                    )
                    self._save_to_s3(crypto_data, s3_path)
                    print(f"Dados históricos de {crypto} salvos com sucesso!")
        
        except Exception as e:
            print(f"Erro ao baixar dados históricos: {e}")
            raise

    def get_real_time_data(self) -> None:
        """Obtém dados em tempo real usando a API da CoinGecko"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        try:
            # Obtém dados de todas as moedas em uma única requisição
            ids = ','.join(self.coingecko_ids.values())
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd&include_24hr_vol=true&include_24hr_high=true&include_24hr_low=true"
            
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                
                for crypto, coingecko_id in self.coingecko_ids.items():
                    try:
                        coin_data = data.get(coingecko_id)
                        if coin_data:
                            latest_data = {
                                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                'price': float(coin_data['usd']),
                                'volume_24h': float(coin_data.get('usd_24h_vol', 0)),
                                'high_24h': float(coin_data.get('usd_24h_high', 0)),
                                'low_24h': float(coin_data.get('usd_24h_low', 0)),
                                'symbol': crypto
                            }
                            
                            # Organiza os dados em pastas separadas para cada ativo
                            symbol_folder = crypto.replace('-USD', '').lower()  # Remove o '-USD' e converte para minúsculo
                            s3_path = f"realtime/{symbol_folder}/{timestamp}.json"
                            self._save_to_s3(latest_data, s3_path)
                            print(f"{crypto}: ${latest_data['price']:.2f}")
                    except Exception as e:
                        print(f"Erro ao processar dados de {crypto}: {e}")
            else:
                print(f"Erro na requisição à API da CoinGecko: {response.status_code}")
                
        except Exception as e:
            print(f"Erro ao obter dados em tempo real: {e}")

    def start_monitoring(self) -> None:
        """Inicia o monitoramento em tempo real"""
        self.download_historical_data()
        
        print("\nIniciando monitoramento em tempo real...")
        while True:
            try:
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print(f"\nAtualizando dados em {current_time}")
                
                self.get_real_time_data()
                time.sleep(60)  # Respeita o limite de taxa da API gratuita da CoinGecko
                
            except Exception as e:
                print(f"Erro durante a execução: {e}")
                time.sleep(60) 