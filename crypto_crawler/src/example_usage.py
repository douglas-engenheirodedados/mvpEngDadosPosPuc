from crawler.coingecko_spider import CoinGeckoSpider
from crawler.historical_data import get_crypto_historical_data
from datetime import datetime, timedelta

# Real-time data from CoinGecko
spider = CoinGeckoSpider()

# Get current prices
prices = spider.get_current_price(
    coins=['bitcoin', 'ethereum'],
    vs_currencies=['usd', 'eur']
)
print("Current prices:", prices)

# Get detailed market data for Bitcoin
btc_data = spider.get_coin_market_data('bitcoin')
print("Bitcoin market data:", btc_data)

# Historical data from Yahoo Finance
start_date = datetime.now() - timedelta(days=365)
btc_historical = get_crypto_historical_data(
    symbol='BTC-USD',
    start_date=start_date,
    interval='1d'
)
print("Bitcoin historical data:\n", btc_historical.head()) 