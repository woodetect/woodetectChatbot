import time
from flask import Flask, request, jsonify
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


control = pyllama()
# Store the generator object
gen_obj = None

@app.route('/get_word', methods=['GET'])
def get_word():
    global gen_obj
    word = ""
    if gen_obj is None:
        gen_obj = control.pyllama_next()
    try:
        word = next(gen_obj)
    except StopIteration:
        gen_obj = None  # Reset the generator if it's reached the end
        word = "STOP"
    return jsonify({"reply": word})

@app.route('/check_wait_input', methods=['GET'])
def check_wait_input():
    return jsonify({"wait_input": control.pyllama_wait_input()})

@app.route('/send_message', methods=['GET', 'POST'])
def send_message():
    message = request.json['message']
    formatted_question = f"###Human: {message}\n###Assistant:"
    control.send(formatted_question)
    return jsonify({"status": "Message sent"})

if __name__ == '__main__':
    app.run(port=80)