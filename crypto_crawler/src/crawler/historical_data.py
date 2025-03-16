import yfinance as yf
import pandas as pd
from datetime import datetime
from typing import Optional, Dict
from pathlib import Path
import json

class HistoricalDataCollector:
    """Coletor de dados históricos para múltiplas criptomoedas."""
    
    CRYPTO_CONFIG = {
        'bitcoin': {
            'symbol': 'BTC-USD',
            'start_year': 2014
        },
        'ethereum': {
            'symbol': 'ETH-USD',
            'start_year': 2015  # Ethereum começou em 2015
        }
    }
    
    def __init__(self):
        self.base_dir = Path("data")

    def get_crypto_historical_data(
        self,
        crypto_name: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        interval: str = "1d"
    ) -> pd.DataFrame:
        """
        Coleta dados históricos de uma criptomoeda específica.
        
        Args:
            crypto_name: Nome da criptomoeda (ex: 'bitcoin', 'ethereum')
            start_date: Data inicial opcional
            end_date: Data final opcional
            interval: Intervalo dos dados
        """
        if crypto_name not in self.CRYPTO_CONFIG:
            raise ValueError(f"Criptomoeda não suportada: {crypto_name}")
            
        config = self.CRYPTO_CONFIG[crypto_name]
        
        if not start_date:
            start_date = datetime(config['start_year'], 1, 1)
        if not end_date:
            end_date = datetime.now()
        
        try:
            crypto = yf.Ticker(config['symbol'])
            df = crypto.history(
                start=start_date,
                end=end_date,
                interval=interval
            )
            df['source'] = 'yahoo_finance'
            return df
        except Exception as e:
            print(f"Erro ao buscar dados históricos de {crypto_name}: {e}")
            return pd.DataFrame()

    def save_historical_data(self, data: pd.DataFrame, crypto_name: str) -> None:
        """Salva dados históricos para uma criptomoeda específica."""
        if data.empty:
            return

        output_dir = self.base_dir / crypto_name / "historical"
        output_dir.mkdir(parents=True, exist_ok=True)

        data_dict = {
            'metadata': {
                'coin': crypto_name,
                'symbol': self.CRYPTO_CONFIG[crypto_name]['symbol'],
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

        filename = output_dir / f"{crypto_name}_historical_complete.json"
        with open(filename, 'w') as f:
            json.dump(data_dict, f, indent=4)
        print(f"Dados históricos de {crypto_name} salvos em: {filename}") 