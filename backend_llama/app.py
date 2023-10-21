import time
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import threading
import re
import warnings
from typing import List

warnings.filterwarnings("ignore", category=UserWarning)

from llamacpp_channel import *

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'
control = pyllamacpp()
gen_obj = control.next_word()

@app.route('/')
@cross_origin()
def status():
    return "chatbot API online." 

@app.route('/is_loading', methods=['GET', 'POST'])
def is_loading():
    tmp = str(control.is_loading())
    return jsonify({"reply": tmp})

@app.route('/get_sentence_history', methods=['GET'])
def get_sentence_history():
    return jsonify({"reply": str(control.get_sentences_history())})

@app.route('/get_last_sentence', methods=['GET', 'POST'])
def get_last_sentence():
    return jsonify({"reply": control.get_last_sentence()})

@app.route('/check_waiting', methods=['GET'])
def check_waiting():
    if control.waiting():
        return jsonify({"reply": "True"})
    return jsonify({"reply": "False"})

@app.route('/check_exited', methods=['GET'])
def check_exited():
    return jsonify({"reply": str(control.exited())})

@app.route('/debug', methods=['GET'])
def debug():
    return jsonify({"waiting": control.waiting(),
                    "exited": control.exited(),
                    "loading": control.is_loading()})

@app.route('/send_message', methods=['GET', 'POST'])
def send_message():
    message = request.json['message']
    formatted_question = f"###Human: {message}\n"
    control.send(formatted_question)
    return jsonify({"reply": "Message sent"})

def llama_cpp_thread():
    global gen_obj
    while True:
        try:
            word = next(gen_obj)
        except  StopIteration:
            print("Anormal stop")

if __name__ == '__main__':
    threading.Thread(target=lambda: app.run(port=5000, debug=True, use_reloader=False)).start()
    llama_cpp_thread()