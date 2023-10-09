import time
from flask import Flask, request
from flask_cors import CORS, cross_origin
import re
import warnings
from typing import List

import torch
import os
from langchain import PromptTemplate
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain.llms import HuggingFacePipeline
from langchain.schema import BaseOutputParser
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    StoppingCriteria,
    StoppingCriteriaList,
    pipeline,
)


warnings.filterwarnings("ignore", category=UserWarning)

MODEL_NAME = "tiiuae/falcon-7b"

model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME, trust_remote_code=True, load_in_8bit=True, device_map="auto"
)
model = model.eval()

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

generation_config = model.generation_config
generation_config.temperature = 0
generation_config.num_return_sequences = 1
generation_config.max_new_tokens = 256
generation_config.use_cache = False
generation_config.repetition_penalty = 1.7
generation_config.pad_token_id = tokenizer.eos_token_id
generation_config.eos_token_id = tokenizer.eos_token_id

print("MODEL READY!")

# Informations sur Woodetect

# Préambule pour initialiser le prompt
preamble = f"""
Woodetect : Lutte contre le trafic de bois
Problème:
Le trafic de bois illégal vaut 150 milliards $/an, entraînant déforestation et corruption.
La solution est Woodetect qui déploie des capteurs acoustiques en forêt pour détecter les activités illégales.
Communication: Transfert d'infos via radio.
Analyse: IA identifiant bruits suspects.
Alerte: Notifications en cas de détection.
Cibles: Gestionnaires de forêts, notamment au Mozambique, Sénégal, et Brésil.
Concept économique: Coût dépendant de la superficie. Maintenance assurée localement avec formation.
Tu est le chatbot de woodetect, répond au questions:
"""

conversation_history = ""

def backup(prompt) -> str:
    return "An error occuredd :("

def falcon_llm(user_input):
    global conversation_history
    print(f"user request |{user_input}|")
    conversation_history += f"Human: {user_input}\nAI: "  # Mise à jour de l'historique
    prompt = preamble + conversation_history  # Mise à jour de l'historique
    input_ids = tokenizer(prompt, return_tensors="pt").input_ids
    input_ids = input_ids.to(model.device)
    with torch.inference_mode():
        outputs = model.generate(input_ids=input_ids, generation_config=generation_config)
    ai_response = tokenizer.decode(outputs[0], skip_special_tokens=True).split("AI: ")[-1]
    conversation_history += ai_response + "\n"
    print("response generated!")
    return ai_response

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
    message = request.json['message']
    try:
        print("generating response...")
        if generation_config.max_new_tokens == 128:
            falcon_response = falcon_llm(message)
        print(f"LLM server response |{falcon_response}|")
    except Exception as e:
        falcon_response = "error:" + str(e)
    return {'reply': falcon_response[1:]}

if __name__ == '__main__':
    app.run(port=80)
