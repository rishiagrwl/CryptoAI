import os
from typing import Union
import json
import openai
from decouple import config as envConfig
from src.utils import *
from pydantic import BaseModel
from src.custom_ratelimit import rate_limit

CONFIG = read_yaml()

# initiate the client
client = openai.OpenAI(
    base_url = CONFIG['TOGETHER_AI_BASE_URL'],
    api_key = envConfig('TOGETHER_AI_API', cast=str),
)  


@rate_limit(calls=CONFIG['LLM_LIMIT_CALLS'], period=CONFIG['LLM_LIMIT_PERIOD'])
## llm call function that can handle non-streaming responses for json and tool calls
def get_llm_response(messages: list = [], system_message: str = None, user_message: str = None, tool_list: list = None, json_schema: BaseModel = None):
    # add system message at start
    if system_message:
        messages = [{'role':'system', 'content':system_message}] + messages[1:]
    # add user message at end
    if user_message:
        messages.append({'role': 'user', 'content':user_message})

    request_params = {
        'model':CONFIG['LLM_MODEL'],
        'messages': messages,
        'max_tokens': 512,
        'temperature': 0.1,
        'top_p': 0.1,
    }

    if tool_list:
        request_params["tools"] = tool_list
        request_params["tool_choice"] = "auto"

    if json_schema:
        request_params["response_format"] = {
            "type": "json_object",
            "schema": json_schema.model_json_schema(),
        }

    # get response from openai+together client
    response = client.chat.completions.create(**request_params)

    # raw text answer
    text_answer = response.choices[0].message.content
    tool_calls = response.choices[0].message.tool_calls
    tools_op = []
    json_answer = {}

    # update tools_op list
    if tool_calls:
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            tools_op.append({'id':tool_call.id,'name':function_name, 'args': function_args})
    
    # get answer in json format
    elif json_schema:
        json_answer = json.loads(text_answer)

    return messages, text_answer, json_answer, tools_op