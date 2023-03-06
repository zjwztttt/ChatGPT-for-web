import os
import openai
from flask import Flask, jsonify, escape, request, render_template

openai.api_key = "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"
user_input="宇宙有多大？"
print(user_input)
completion = openai.ChatCompletion.create(
  model="gpt-3.5-turbo",
  messages=[
    {
        "content": user_input,
        "role": "assistant"
    }
  ]
)
output_text = completion.choices[0].message.content
print(output_text)
