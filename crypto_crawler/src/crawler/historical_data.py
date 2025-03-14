import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional

def get_crypto_historical_data(
    symbol: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    interval: str = "1d"
) -> pd.DataFrame:
    """
    Coleta dados históricos de criptomoedas do Yahoo Finance.
    Fornece dados completos desde 2014 ou data especificada.
    
    Args:
        symbol: Símbolo da criptomoeda (ex: 'BTC-USD')
        start_date: Data inicial para coleta (default: 01/01/2014)
        end_date: Data final para coleta (default: data atual)
        interval: Intervalo dos dados ('1d', '1h', '15m', etc.)
    
    Returns:
        DataFrame com dados históricos de preço e volume
    """
    # Define data inicial padrão como 2014 se não especificada
    if not start_date:
        start_date = datetime(2014, 1, 1)
    # Define data final padrão como atual se não especificada
    if not end_date:
        end_date = datetime.now()
    
    try:
        # Inicializa objeto Ticker do Yahoo Finance
        crypto = yf.Ticker(symbol)
        
        # Coleta dados históricos com parâmetros especificados
        df = crypto.history(
            start=start_date,
            end=end_date,
            interval=interval
        )
        
        # Adiciona coluna de fonte para rastreabilidade
        df['source'] = 'yahoo_finance'
        return df
    except Exception as e:
        print(f"Error fetching historical data: {e}")
        return pd.DataFrame()  # Retorna DataFrame vazio em caso de erro 