import requests
from datetime import datetime
import json

def fetch_realtime_price(coin_id: str) -> dict:
    url = f"https://api.coingecko.com/api/v3/simple/price"
    params = {
        'ids': coin_id,
        'vs_currencies': 'usd',
        'include_market_cap': 'true',
        'include_24hr_vol': 'true',
        'include_24hr_change': 'true'
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise Exception(f"Error fetching data from CoinGecko: {response.text}")
    
    price_data = response.json()[coin_id]
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    
    return {
        "coin": coin_id,
        "timestamp": timestamp,
        "price_usd": price_data.get('usd'),
        "market_cap_usd": price_data.get('usd_market_cap'),
        "volume_24h": price_data.get('usd_24h_vol'),
        "change_24h_percent": price_data.get('usd_24h_change'),
        "source": "CoinGecko"
    }
