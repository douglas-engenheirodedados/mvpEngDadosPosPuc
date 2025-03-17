import yfinance as yf
from datetime import datetime

def fetch_crypto_history(ticker: str, coin_name: str, start_date: str = '2014-01-01') -> dict:
    data = yf.Ticker(ticker).history(start=start_date)
    
    if data.empty:
        raise ValueError(f"No data found for {ticker}")

    data_dict = data.to_dict(orient='index')
    formatted_data = []
    for date_obj, row in data_dict.items():
        formatted_data.append({
            "date": date_obj.strftime('%Y-%m-%d'),
            "open": round(row.get('Open', 0), 2) if row.get('Open') is not None else None,
            "high": round(row.get('High', 0), 2) if row.get('High') is not None else None,
            "low": round(row.get('Low', 0), 2) if row.get('Low') is not None else None,
            "close": round(row.get('Close', 0), 2) if row.get('Close') is not None else None,
            "volume": int(row.get('Volume', 0)) if row.get('Volume') is not None else None,
            "source": "yahoo_finance"
        })

    metadata = {
        "coin": coin_name,
        "source": "Yahoo Finance",
        "start_date": formatted_data[0]["date"],
        "end_date": formatted_data[-1]["date"],
        "data_points": len(formatted_data),
        "created_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    return {
        "metadata": metadata,
        "data": formatted_data
    }
