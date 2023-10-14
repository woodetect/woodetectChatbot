import time
from subprocess import Popen, PIPE, STDOUT
from flask import Flask, request
from flask_cors import CORS, cross_origin
import re
import warnings
from typing import List

from langchain import PromptTemplate
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain.llms import HuggingFacePipeline
from langchain.schema import BaseOutputParser

warnings.filterwarnings("ignore", category=UserWarning)

woodetect = """
""" # empty if fine-tuned

def parse_dumb_response(answer):
    # need to be in proper order
    dumb = ["llama_print_timings"]
    surplus = ["client", "bot", "user", "system", "user:", "bot:", "system:", "client:"]
    text = answer.lower()
    for d in dumb:
        pos = text.find(d)
        if pos != -1:
            print(f"found {d} at {pos}")
            text = text[:pos]
    for s in surplus:
        pos = text.rfind(s)
        if pos != -1:
            text = text[:pos]
    if text == "":
        print("regeneration...")
        text = llama_cpp_call(woodetect, instruction, answer)
    return text

def llama_cpp_call(conversation, user_msg):
    prefix = "Bot:"
    prompt = f"{conversation}\n{user_msg}\n{prefix}"
    # Command and parameters as a list
    command = [
        "./llama.cpp/main",
        "-m", "./llama.cpp/ggml-model-q4_0.gguf",
        "--temp", "0.2",
        "--ctx-size", "2048",
        "--frequency-penalty", "1.4",
        "--presence-penalty", "1.4",
        "-p", prompt,
        "-n", "128"
    ]
    process = Popen(command, stdout=PIPE, stderr=STDOUT)
    stdout, stderr = process.communicate()
    utf = stdout.decode('utf-8')
    pos_start = utf.find(prefix) + len(prefix)
    if pos_start != -1:
        utf = utf[pos_start:]
    utf = parse_dumb_response(utf)
    return utf, stderr

def write_log(text):
    with open("log.txt", "a") as f:
        f.write(text + "\n")

instruction = "" # no need if fine-tuned

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

conversation_arr = []
conversation = ""

@app.route('/')
@cross_origin()
def get_status():
    return "online" 

@app.route('/send_message', methods=['GET', 'POST'])
@cross_origin()
def send_message():
    global conversation
    global conversation_arr
    system_prompt = f"{woodetect}\n{instruction}:\n"
    if len(conversation_arr) == 0:
        conversation_arr.append(system_prompt)
    user_msg = "\nUser: " + request.json['message'] + "\n"
    conversation_arr.append(user_msg)
    #for conv in conversation_arr:
    #    conversation += conv
    conversation = system_prompt + conversation_arr[-1]
    print(f"conversation: {conversation}")
    try:
        print("generating response...")
        llm_response, _ = llama_cpp_call(conversation, user_msg)
        print(f"LLM server response |{llm_response}|")
    except Exception as e:
        write_log(e)
    llm_response = "Bot: " + llm_response
    if "llama" in llm_response:
        print("Fatal error:", llm_response)
        write_log(llm_response)
        llm_response = "A problem occured with the LLM server. Please try again later."
    conversation_arr.append(llm_response)
    return {'reply': llm_response}

if __name__ == '__main__':
    app.run(port=80)