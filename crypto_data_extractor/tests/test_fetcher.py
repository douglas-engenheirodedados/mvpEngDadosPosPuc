from src.fetcher import fetch_crypto_history

def test_fetch_btc():
    data = fetch_crypto_history("BTC-USD", "bitcoin", start_date="2023-01-01")
    assert "metadata" in data
    assert "data" in data
    assert data["metadata"]["coin"] == "bitcoin"
