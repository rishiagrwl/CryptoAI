from src.crypto_data import get_crypto_ids, get_cached_crypto_price, get_supported_currs, fetch_crypto_ids_api, fetch_supported_curr_api
from src.utils import *
import uuid
from src.llm_call import get_llm_response
from src.translate import translate_text, ISO_code
from custom_logging import crypto_logger
import os

CONFIG = read_yaml()

# create logs folder if not exist already
if not os.path.exists('logs'):
    os.makedirs('logs')

# load the stored data of supported currency and crypto ids
supported_curr = get_supported_currs()
crypto_id_map = get_crypto_ids()

# load the prev conversations
conv_hist = read_json(input_file=CONFIG['CONV_HIST_JSON'])

# define the tools
useful_tools = [
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
            "description": "The crypto id, e.g. bitcoin, monke, etc.",
            # "enum": crypto_ids,
            # "enum":["bitcoin", "ethereum", "dogecoin"],
          },
          "currency": {
            "type": "string",
            "description": "The currency of the crypto price, e.g. usd, eur, etc.",
            # "enum": supported_curr,
            # "enum": ["usd", "eur", "gbp"],
          }
        },
        "required": ["crypto_id"],
      }
    }
  },
]

# define the system prompts
SYS_PROMPT_TOOLS = '''
You are a helpful assistant. You are provided with some functions which you can use to get answer for user query. In the end provide a final answer to user, no details of function should be included.
For other queries which are not related to provided functions, refuse to give the answer politely by saying that you are only designed to answer questions related to the functions you are provided with.
DO NOT give any suggestions for other queries.
'''

SYS_PROMPT_LANGUAGE = '''
You are a helpful assistant. Your task is to identify the language of the user message and provide its ISO 639-1 code. Only answer in JSON.
'''
# checks if user_id alreadu exists or not
def check_username(user_id: str):
   if user_id not in conv_hist:
      return "Username submitted successfully"
   else:
      return "Username already exists, its conversation history will be used, if not intended, please change the username"
   
# re-fetch supported_curr
def refetch_curr():
  supp_curr = fetch_supported_curr_api()
  crypto_logger.info(f"Fetching supported currencies from url")
  write_json(data=supp_curr, output_file=CONFIG['CURR_JSON'])
  return "Refetched currencies succesfully"

# re-fetch crypto_ids_map
def refetch_crypto_ids():
  crypto_ids = fetch_crypto_ids_api()
  crypto_logger.info(f"Fetching crypto ids from url")
  write_json(data=crypto_ids, output_file=CONFIG['CRYPTO_ID_JSON'])
  return "Refetched currencies succesfully"

# loads prev conversation for the given user_id just removes the tool call conv
def get_conv_hist(user_id: str):
    if user_id not in conv_hist:
        conv_hist[user_id] = []
    new_conv = []
    for conv in conv_hist[user_id]:
       if conv['role'] != 'tool':
          new_conv.append(conv)
    return new_conv

def get_response(user_query: str, user_id: str):
    crypto_logger.info(f'------------------------------------------NEW RUN----------------------------------------------------------')
    
    # a unique id for each ques, useful for tracing each ques
    unique_id = uuid.uuid4().hex
    crypto_logger.info(f'{user_id} | {unique_id} | USER QUERY: {user_query}')
    
    # find the user query kanguage and get english text if not already
    trans_msg, trans_text_answer, trans_json_answer, trans_tools_op = get_llm_response(system_message=SYS_PROMPT_LANGUAGE, user_message=user_query, json_schema=ISO_code)
    crypto_logger.info(f'{user_id} | {unique_id} | TRANSLATE LLM RESPONSE: msgs-{trans_msg}, text answer-{trans_text_answer}, json answer-{trans_json_answer}, tool calls-{trans_tools_op}')
    print(type(trans_json_answer))
    if trans_json_answer['ISO_code'] != 'en':
        user_query = translate_text(text = user_query, source=trans_json_answer['ISO_code'])
        crypto_logger.info(f'{user_id} | {unique_id} | TRANSLATED USER QUERY: {user_query}')
   
   # past conv loading
    past_conv = get_conv_hist(user_id=user_id)
    crypto_logger.info(f'{user_id} | {unique_id} | Past conversation fetched')
    
    # get first reponse for user query
    msgs, text_answer, json_answer, tools_op = get_llm_response(messages=past_conv, system_message=SYS_PROMPT_TOOLS, user_message=user_query, tool_list=useful_tools)
    crypto_logger.info(f'{user_id} | {unique_id} | LLM RESPONSE: msgs-{msgs[-3:]}, text answer-{text_answer}, json answer-{json_answer}, tool calls-{tools_op}')
    
    # run the loop until all llm stops giving tool calls
    while tools_op:
      for tool in tools_op:
        if tool['name']=='get_crypto_price':
          func_response = get_cached_crypto_price(crypto_id=tool['args']['crypto_id'].lower(), currency=tool['args']['currency'].lower(), supported_curr=supported_curr, crypto_id_map=crypto_id_map, user_id=user_id, quuid=unique_id)
          crypto_logger.info(f'{user_id} | {unique_id} | FUNCTION RESPONSE: {func_response}')
          msgs.append(
                        {
                          "tool_call_id": tool['id'],
                          "role": "tool",
                          "name": tool['name'],
                          "content": str(func_response),
                        }
                    )
        else:
          crypto_logger.error(f"No function exist as {tool['name']}")
          raise ValueError(f"No function exist as {tool['name']}")
      
      msgs, text_answer, json_answer, tools_op = get_llm_response(messages=msgs)
      crypto_logger.info(f'{user_id} | {unique_id} | LLM RESPONSE: msgs-{msgs[-3:]}, text answer-{text_answer}, json answer-{json_answer}, tool calls-{tools_op}')
    
    # append the final text answer
    msgs.append(
                {
                  "role": "assistant",
                  "content": text_answer,
                }
            )
    
    # translate back the answer if user query was in some other language
    if trans_json_answer['ISO_code'] != 'en':
      final_answer = translate_text(text=text_answer, target=trans_json_answer['ISO_code'])
    else: 
      final_answer = text_answer
    
    crypto_logger.info(f'{user_id} | {unique_id} | FINAL ANSWER: {final_answer}')
    
    # update and save the conversation for this user
    conv_hist[user_id]=msgs
    write_json(data=conv_hist, output_file=CONFIG['CONV_HIST_JSON'])
    
    crypto_logger.info(f'{user_id} | {unique_id} | Updated conversation stored')
    return final_answer


