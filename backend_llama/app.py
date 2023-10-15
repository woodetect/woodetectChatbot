import time
from flask import Flask, request
from flask_cors import CORS, cross_origin
import re
import warnings
from typing import List

warnings.filterwarnings("ignore", category=UserWarning)

from interference_channel import *

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/')
@cross_origin()
def get_status():
    return "online" 

@app.route('/send_message', methods=['GET', 'POST'])
@cross_origin()
def send_message():
    user_msg = "\nUser: " + request.json['message'] + "\n"
    try:
        print("generating response...")
        llm_response, _ = llama_cpp_call(user_msg, user_msg)
    except Exception as e:
        write_log(e)
    return {'reply': llm_response}

if __name__ == '__main__':
    app.run(port=80)