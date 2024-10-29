import time
import requests
from src.utils import *
from custom_logging import crypto_logger

CONFIG = read_yaml()

## fetch all currencies supported by coingecko
def fetch_supported_curr_api():
    url = CONFIG['VS_CURR_ID']
    try:
        response = requests.get(url)
        # Check for HTTP errors
        response.raise_for_status()
        data = response.json()
        crypto_logger.info("Supported currencies fetched successfully")
        return data
    except requests.exceptions.RequestException as e:
        crypto_logger.error(f"Error fetching supported currencies: {e}")

## function to load supported currs
def get_supported_currs():
    crypto_ids = read_json(input_file=CONFIG['CURR_JSON'])

    if not crypto_ids:
        crypto_ids = fetch_supported_curr_api()
        crypto_logger.info(f"Fetching supported currencies from url")
        write_json(data=crypto_ids, output_file=CONFIG['CURR_JSON'])

    crypto_logger.info(f"Total supported currencies fetched: {len(crypto_ids)}")
    return crypto_ids

## fetch crypto ids from api
def fetch_crypto_ids_api():
    url = CONFIG['CRYPTO_ID_URL']
    try:
        response = requests.get(url)
        # Check for HTTP errors
        response.raise_for_status()
        data = response.json()
        crypto_logger.info("Crypto IDs fetched successfully")
        return data
    
    except requests.exceptions.RequestException as e:
        crypto_logger.error(f"Error fetching crypto IDs: {e}")

## function to load crypto_ids
def get_crypto_ids():
    crypto_ids = read_json(input_file=CONFIG['CRYPTO_ID_JSON'])

    if not crypto_ids:
        crypto_ids = fetch_crypto_ids_api()
        crypto_logger.info(f"Fetching crypto ids from url")
        write_json(data=crypto_ids, output_file=CONFIG['CRYPTO_ID_JSON'])

    crypto_logger.info(f"Total crypto ids fetched: {len(crypto_ids)}")
    return crypto_ids

## fetch real time price for given crypto_id and currency
def fetch_crypto_price_api(crypto_id='bitcoin', currency='usd'):
    crypto_price_endpoint = CONFIG['CRYPTO_PRICE_ENDPOINT']
    url = f'{crypto_price_endpoint}?ids={crypto_id}&vs_currencies={currency}'
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check for HTTP errors
        data = response.json()
        price = data[crypto_id][currency]
        crypto_logger.info(f"Price fetched for {crypto_id.capitalize()} is {price} {currency.upper()}")
        return price
    except requests.exceptions.RequestException as e:
        crypto_logger.error(f"Error fetching price data: {e}")

## check cache before calling the crypto api
def get_cached_crypto_price(crypto_id='bitcoin', currency='usd'):
    # load the cache
    cache = read_json(input_file=CONFIG['CACHE_JSON'])
    # fetch the cache limit (in secs)
    cache_expiry = CONFIG['CACHE_LIMIT']
    current_time = time.time()

    if not (crypto_id in cache):
        cache[crypto_id] = {}

    # check if already present in cache
    if (currency in cache[crypto_id]) and (current_time - cache[crypto_id][currency]['time'] < cache_expiry):
        price =  cache[crypto_id][currency]['price']
    
    # Otherwise, fetch the new price
    else:
        price = fetch_crypto_price_api(crypto_id, currency)
        cache[crypto_id][currency] = {'price': price, 'time': current_time}
        write_json(data=cache, output_file=CONFIG['CACHE_JSON'])

    # ## return a formatted answer
    # return f"The current price of {crypto_id.capitalize()} is {price} {currency.upper()}."
    return price
