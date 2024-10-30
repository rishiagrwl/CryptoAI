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
        if response.status_code == 429:  # Too Many Requests
            print("Rate limit exceeded. Waiting for 60 seconds...")
            crypto_logger.info("Rate limit exceeded. Waiting for 60 seconds...")
            time.sleep(60)
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
    supp_curr = read_json(input_file=CONFIG['CURR_JSON'])

    if not supp_curr:
        supp_curr = fetch_supported_curr_api()
        crypto_logger.info(f"Fetching supported currencies from url")
        write_json(data=supp_curr, output_file=CONFIG['CURR_JSON'])

    crypto_logger.info(f"Total supported currencies fetched: {len(supp_curr)}")
    return supp_curr

## fetch crypto ids from api
def fetch_crypto_ids_api():
    url = CONFIG['CRYPTO_ID_URL']
    try:
        response = requests.get(url)
        if response.status_code == 429:  # Too Many Requests
            print("Rate limit exceeded. Waiting for 60 seconds...")
            crypto_logger.info("Rate limit exceeded. Waiting for 60 seconds...")
            time.sleep(60)
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

## validate crypto parameters from LLM
def validate_crypto_params(crypto_id: str, currency: str, supported_curr: list, crypto_id_map: list):
    crypto_ids = [crypto['id'].lower().strip() for crypto in crypto_id_map]
    crypto_symbols = [crypto['symbol'].lower().strip() for crypto in crypto_id_map]
    crypto_names = [crypto['name'].lower().strip() for crypto in crypto_id_map]
    supported_curr = [curr.lower().strip() for curr in supported_curr]
    crypto_id = crypto_id.lower().strip()
    if currency:
        currency = currency.lower().strip()
    else:
        currency = 'usd'

    # Check if crypto_id or symbol is valid
    if crypto_id not in crypto_ids and crypto_id not in crypto_symbols and crypto_id not in crypto_names:
        crypto_logger.error(f"Invalid crypto_id or symbol or name: '{crypto_id}'. Please choose a valid one.")
        raise ValueError(f"Invalid crypto_id or symbol or name: '{crypto_id}'. Please choose a valid one.")
    else: 
        if crypto_id in crypto_ids: crypto_final_id= crypto_id
        elif crypto_id in crypto_symbols: crypto_final_id= crypto_ids[crypto_symbols.index(crypto_id)]
        elif crypto_id in crypto_names: crypto_final_id= crypto_ids[crypto_names.index(crypto_id)]
    
    # Check if currency is valid
    if currency not in supported_curr:
        crypto_logger.error(f"Invalid currency: '{currency}'. Supported currencies are {supported_curr}")
        raise ValueError(f"Invalid currency: '{currency}'. Supported currencies are {supported_curr}")
    
    return crypto_final_id, currency

## fetch real time price for given crypto_id and currency
def fetch_crypto_price_api(crypto_id='bitcoin', currency='usd'):
    crypto_price_endpoint = CONFIG['CRYPTO_PRICE_ENDPOINT']
    url = f'{crypto_price_endpoint}?ids={crypto_id}&vs_currencies={currency}'
    try:
        response = requests.get(url)
        if response.status_code == 429:  # Too Many Requests
            print("Rate limit exceeded. Waiting for 60 seconds...")
            crypto_logger.info("Rate limit exceeded. Waiting for 60 seconds...")
            time.sleep(60)
            response = requests.get(url)
        response.raise_for_status()  # Check for HTTP errors
        data = response.json()
        crypto_logger.info(f"Data fetched from cryptoprice api: {data}")
        if not data:
            raise ValueError(f"{crypto_id} price for currency {currency} not available on Coingecko api")
        price = data[crypto_id][currency]
        return price
    except requests.exceptions.RequestException as e:
        crypto_logger.error(f"Error fetching price data: {e}")

## check cache before calling the crypto api
def get_cached_crypto_price(crypto_id='bitcoin', currency='usd', supported_curr=[], crypto_id_map=[], user_id=None, quuid=None):
    # validate first
    crypto_id, currency = validate_crypto_params(crypto_id=crypto_id, currency=currency, supported_curr=supported_curr, crypto_id_map=crypto_id_map)
    crypto_logger.info(f'{user_id} | {quuid} | After validation: crypto_id: {crypto_id}, currency: {currency}')
    # load the cache
    cache = read_json(input_file=CONFIG['CACHE_JSON'])
    # fetch the cache limit (in secs)
    cache_expiry = CONFIG['CACHE_LIMIT']
    current_time = time.time()

    if not (crypto_id in cache):
        cache[crypto_id] = {}
        crypto_logger.info(f'{user_id} | {quuid} | Crypto id not present in cache: {crypto_id}')


    # check if already present in cache
    if (currency in cache[crypto_id]) and (current_time - cache[crypto_id][currency]['time'] < cache_expiry):
        price =  cache[crypto_id][currency]['price']
    
    # Otherwise, fetch the new price
    else:
        crypto_logger.info(f'{user_id} | {quuid} | Currency {currency} not present in {crypto_id} cache or price expired')
        price = fetch_crypto_price_api(crypto_id, currency)
        cache[crypto_id][currency] = {'price': price, 'time': current_time}
        write_json(data=cache, output_file=CONFIG['CACHE_JSON'])

    # ## return a formatted answer
    # return f"The current price of {crypto_id.capitalize()} is {price} {currency.upper()}."
    return json.dumps({'crypto_id':crypto_id, 'current_price':f'{price} {currency}'})
