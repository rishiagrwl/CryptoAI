import os
import json
import openai
from decouple import config as envConfig
from custom_logging import crypto_logger
from src.utils import *
from src.crypto_data import get_supported_currs, get_crypto_ids, get_cached_crypto_price

CONFIG = read_yaml()

client = openai.OpenAI(
    base_url = CONFIG['TOGETHER_AI_BASE_URL'],
    api_key = envConfig('TOGETHER_AI_API', cast=str),
)  

def get_llm_response(system_msg: str=None, user_msg: str=None, tool_list: list = None):
    messages = [
        {'role':'system', 'content':system_msg},
        {'role': 'user', 'content':user_msg}
    ]

    response = client.chat.completions.create(
        model=CONFIG['LLM_MODEL'],
        messages=messages,
        tools=tool_list,
        tool_choice="auto",
    )
    print(response)
    tool_calls = response.choices[0].message.tool_calls
    if tool_calls:
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            if function_name == "get_crypto_price":
                function_response = get_cached_crypto_price(
                    crypto_id=function_args.get("crypto_id"),
                    currency=function_args.get("currency"),
                )
                print(function_response)

                messages.append(
                    {
                        "role": "assistant",
                        "content": f"Calling {function_name} with {function_args}"
                    }
                )
                # messages.append(
                #     {
                #         "tool_call_id": tool_call.id,
                #         "role": "ipython",
                #         "name": function_name,
                #         "content": str(function_response),
                #     }
                # )

            function_enriched_response = client.chat.completions.create(
                model=CONFIG['LLM_MODEL'],
                messages=messages,
                # tools=tool_list,
                # tool_choice="auto"
            )
            print(json.dumps(function_enriched_response.choices[0].message.model_dump(), indent=2))

    else:
        raise ValueError("Didn't call function")