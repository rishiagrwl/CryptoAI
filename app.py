from src.crypto_data import fetch_crypto_ids_api, get_crypto_ids, fetch_crypto_price_api, get_cached_crypto_price

crypto_ids = get_crypto_ids()
print(len(crypto_ids))

answer = get_cached_crypto_price()
print(answer)