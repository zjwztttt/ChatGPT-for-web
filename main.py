# pip install openai
# 引入OpenAI包
# 引入Flask web包
# 引入markupsafe的escape方法防止web输入端的恶意注入
import openai
import os
from flask import Flask
from markupsafe import escape

openai.api_key = ''

response = openai.Completion.create(
    model='text-davinci-003',
    prompt='主题：早餐 风在\n两句话的冒险故事',
    temperature=0.8,
    max_tokens=500,
    top_p=1.0,
    frequency_penalty=0.5,
    presence_penalty=0.0,
)
print(response.choices[0].text)
