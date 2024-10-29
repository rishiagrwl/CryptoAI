from src.crypto_data import get_crypto_ids, get_cached_crypto_price, get_supported_currs

# crypto_ids = get_crypto_ids()
# print(len(crypto_ids))

# answer = get_cached_crypto_price()
# print(answer)

# currs= get_supported_currs()
# print(currs)

from crypto_AI.src.llm_call import get_llm_response

supported_curr = get_supported_currs()
crypto_id_map = get_crypto_ids()
crypto_ids = [item['id'] for item in crypto_id_map]

tools = [
  {
    "type": "function",
    "function": {
      "name": "get_crypto_price",
      "description": "Get the current crypto price for the given crypto_id and currency",
      "parameters": {
        "type": "object",
        "properties": {
          "crypto_id": {
            "type": "string",
            # "description": "The crypto_id, e.g. bitcoin, monke, etc.",
            # "enum": crypto_ids,
            "enum":["bitcoin", "ethereum", "dogecoin"],
          },
          "currency": {
            "type": "string",
            # "description": "The currency of the crypto price.",
            # "enum": supported_curr,
            "enum": ["usd", "eur", "gbp"],
          }
        },
        "required": ["crypto_id"],
      }
    }
  }
]

messages = [
    {"role": "system", "content": "You are a helpful assistant. You are provided with a function named 'get_crypto_price' if you get any user query related to price of any crypto, call that function, for other queries refuse to give the answer politely by saying that you are only designed to answer crypto price related questions, do not give any suggestions."},
    {"role": "user", "content": "What is Mumbai culture"}
]

get_llm_response(system_msg=messages[0]['content'], user_msg=messages[1]['content'], tool_list=tools)