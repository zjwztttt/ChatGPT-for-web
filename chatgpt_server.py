# 引入依赖包
from flask import Flask, jsonify, escape, request, render_template
import openai
import requests
import toml
import logging
import re
import base64
#import os

# 读取配置文件
with open("config.toml", "r", encoding='utf-8') as f:
    config = toml.load(f)

# 获取配置项
chatgpt_user = config['WEBUI']['chatgpt_user']
web_host = config['WEBUI']['web_host']
web_port = config['WEBUI']['web_port']
server_debug = config['servers']['server_debug']
openai.api_key = config['servers']['Api_key']
text_model = config['servers']['text_model']
code_model = config['servers']['code_model']
image_keyword = config['servers']['image_keyword']

# 创建一个Flask app 应用实例
app = Flask(__name__, static_folder='templates')

# 对用户输入的消息进行过滤和校验
def validate_input(user_input):
    # 使用正则表达式过滤非法字符
    pattern = re.compile(r"[^\w\s]")
    filtered_text = re.sub(pattern, "", user_input)
    if len(filtered_text) < 1:
        raise ValueError("输入的消息不能为空！")
    elif len(filtered_text) > 1024:
        raise ValueError("输入的消息过长，请输入不超过1024个字符的消息！")
    return filtered_text

#定义主页路由和函数
@app.route('/')
def index():
    return render_template('index.html')

# 定义请求的路径和方法
@app.route('/chat', methods=['POST'])
def chatgpt():
    try:
        # 获取 前端页面的请求
        user_input = request.json['text']
        # 对消息进行过滤和校验
        filtered_message = validate_input(user_input)
        
        # 配置 logging
        logging.basicConfig(filename='chatbot.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        # 添加日志记录
        logging.info(f"User input: {filtered_message}")
    
        if filtered_message in image_keyword:
            #生成图像
            response = openai.Image.create(
                prompt=filtered_message,
                n=1,
                size="1024x1024"
            )
            #获取图片URL
            image_url = response['data'][0]['url'].strip()
            if requests.get(image_url).url.startswith('https://'):
                print(image_url)
                # 下载图片
                #image_content = requests.get(image_url).content
                # 将图片转换成Base64编码
                #img_str = base64.b64encode(image_content).decode('utf-8')
                #print("你将图片转换成的Base64编码是：",img_str)
                # 添加日志记录
                logging.info(f"Response: {image_url}")
                return jsonify({'code': 200, 'type': 'image', 'message': image_url})
            else:
                print("图片链接不安全")
        else:
            #生成文字
            completion = openai.ChatCompletion.create(
                model=text_model,
                messages=[
                    {
                        "role": chatgpt_user,
                        "content": filtered_message
                    }
                ],
                temperature=0.9,
                max_tokens=1024,
                top_p=1.0,
                n=1,
                frequency_penalty=0.5,
                presence_penalty=0.0,
            )
            output_user = completion.choices[0].message.role
            print(output_user)
            output_text = completion.choices[0].message.content
            print(output_text)
            
            # 判断是否为代码
            lang, code = detect_code(output_text)
            if lang:
                # 添加日志记录
                logging.info(f"Response: {code}")
                # 如果是代码，则返回代码类型和代码内容
                print("这是代码回复")
                return jsonify({'code': 200, 'type': 'code', 'lang': lang, 'message': code})
            else:
                # 添加日志记录
                logging.info(f"Response: {output_text}")
                # 如果不是代码，则返回普通文本内容
                print("这是文本回复")
                return jsonify({'code': 200, 'type': 'text', 'user': output_user, 'message': output_text})
                
    except Exception as e:
        # 返回错误信息
        return jsonify({'error': str(e)})

# 储存常见语言的正则
def detect_code(text):
    # 正则表达式匹配常见编程语言的语法结构
    patterns = {
        'Java': r'\b(public|private|protected)\s+class\s+\w+\s*{',
        'C': r'\b(int|float|double|char|void)\s+\w+\s*\(',
        'C#': r'\b(public|private|protected)\s+class\s+\w+\s*{',
        'Go': r'\b(func)\s+\w+\(',
        # 可以添加其他语言的正则表达式
    }
    for lang, pattern in patterns.items():
        if re.search(pattern, text):
            return lang, text
    return None, text

# Run the app
if __name__ == '__main__':
    app.run(
        host=web_host,
        port=web_port,
        debug=server_debug,
        load_dotenv=False,#False OR True
#        options = {
#        'ssl_context': None,
#        'threaded': False,#False OR True
#        'processes': None#默认是None
#        }
    )
