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
    Get historical cryptocurrency data from Yahoo Finance
    
    Args:
        symbol: Cryptocurrency symbol (e.g., 'BTC-USD')
        start_date: Start date for historical data
        end_date: End date for historical data
        interval: Data interval ('1d', '1h', '15m', etc.)
    
    Returns:
        DataFrame with historical price data
    """
    if not start_date:
        start_date = datetime(2014, 1, 1)
    if not end_date:
        end_date = datetime.now()
    
    try:
        crypto = yf.Ticker(symbol)
        df = crypto.history(
            start=start_date,
            end=end_date,
            interval=interval
        )
        df['source'] = 'yahoo_finance'
        return df
    except Exception as e:
        print(f"Error fetching historical data: {e}")
        return pd.DataFrame() 