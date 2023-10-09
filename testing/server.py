import time
from flask import Flask, request
from flask_cors import CORS, cross_origin
import re
import warnings
from typing import List

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
    return {'reply': "Comment vas-tu ?"}

if __name__ == '__main__':
    app.run(port=8080)