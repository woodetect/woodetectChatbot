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
Woodetect est une startup française qui développe des solutions technologiques pour lutter contre le trafic de bois illégal. Notre première solution est un système de surveillance autonome qui détecte les activités suspectes dans les forêts et alerte les autorités en temps réel.
Problème: Trafic de bois illégal pèse 150 milliards de dollars/an, menace les forêts mondiales, et entraîne des conséquences sociales et environnementales graves. Peu de pays ont les ressources pour lutter efficacement.
Solution:
Détection: Capteurs acoustiques autonome capable de reconnaitre plusieurs sons (tronçonneuse, oiseaux, camions, animaux...).
Communication: Capteurs reliés par radio à un dispositif connecté à Internet.
Analyse: IA entraînée pour distinguer les bruits anormaux.
Alerte: Notifications en temps réel sur une application et un site internet.
Cibles: États, organismes certificateurs de bois, pays en développement.
Concept économique: Coût basé sur la taille de la zone à surveiller. Formation gratuite pour la maintenance locale.
Installation:
L’application Woodetect sera disponible sur le Play store et à l’avenir sur l’Apple Store.
Un lien permettant d’y accéder sera disponible sur le site vitrine ainsi que sur le site principal
FAQ:
Qui est derrière Woodetect ? Woodetect est créée par 9 étudiants de l’EPITECH.
Comment s’installe le capteur ? Le capteur sera fourni avec une notice d’installation mais l’utilisateur à la possibilité de demander une installation par un professionnel.
Comment recevoir les alertes ? Les notifications sont envoyées automatiquement par mail en cas d’alerte et par notification si l’application est installée
Comment est alimenté le capteur ? Le capteur est alimenté par des batteries de 9V rechargeable par le solaire.
Comment sont gérées les données personnelles ? Nous respectons le RGPD et mettons tout en place pour assurer la sécurité des informations personnelles.
Pour toute questions supplémentaires, nous possédons un mail de contact.

email contact : contact@woodetect.com
site : https://www.woodetect.com/
tél : 06 03 98 60 75
"""

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

instruction = "Conversation entre un commercial et un utilisateur potentiel intéressé par le produit. L'utilisateur pose des questions et le commercial y répond. Directives pour le modèle: Répondez de manière concise et précise aux questions de l'utilisateur. Si vous ne savez pas, indiquez-le clairement."

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