import re
import warnings
from typing import List

import torch
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

MODEL_NAME = "tiiuae/falcon-7b-instruct"

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

# Informations sur Woodetect
woodetect_info = """
Woodetect: Outil de lutte contre le trafic de bois.

Problème:
Le trafic de bois illégal est une industrie de près de 150 milliards de dollars par an, menaçant les forêts et alimentant la déforestation, la corruption, et d'autres activités criminelles. Ce trafic impacte les droits des peuples autochtones et génère des conséquences environnementales et sociales. De nombreux pays n'ont pas les ressources nécessaires pour lutter contre cela.
"""

# Préambule pour initialiser le prompt
preamble = f"""
The following is a friendly conversation between a human and an AI. The AI is
make short answer in french and provides lots of specific details from its context.
Here's some context about Woodetect: {woodetect_info}

Current conversation:
"""

# Historique de conversation initial
conversation_history = ""

while True:
    user_input = input("Vous: ")  # Récupérer l'input utilisateur
    conversation_history += f"Human: {user_input}\nAI: "  # Mise à jour de l'historique

    # Préparation du prompt pour le modèle
    prompt = preamble + conversation_history

    input_ids = tokenizer(prompt, return_tensors="pt").input_ids
    input_ids = input_ids.to(model.device)

    with torch.inference_mode():
        outputs = model.generate(input_ids=input_ids, generation_config=generation_config)

    ai_response = tokenizer.decode(outputs[0], skip_special_tokens=True).split("AI: ")[-1]  # Récupérer la dernière réponse
    print(f"AI: {ai_response}")  # Afficher la réponse

    conversation_history += ai_response + "\n"  # Mise à jour de l'historique

    continue_chat = input("Voulez-vous continuer la conversation? (Oui/Non): ").strip().lower()
    if continue_chat == "non":
        break