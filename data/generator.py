
import os
import csv
import openai
from colorama import Fore
import random

openai.api_key = "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"

PRESENTATION_FILE = "presentation-short.txt"

def get_gpt_answer(feed, conversation, model="gpt-3.5-turbo", t=0.4) -> str:
    """
    Generates a response using OpenAI's GPT-3.5 model based on the given conversation history.
    Args:
        feed (str): The user's input to the conversation.
        conversation (list): A list of dictionaries representing the conversation history.
        model (str, optional): The name of the GPT-3.5 model to use. Defaults to "gpt-3.5".
    Returns:
        str: The response generated by the GPT-3.5 model.
    """
    if feed == conversation[-1]['content']:
        # avoid loop on conversation history problems
        return "(user didnt enter anything)"
    conversation.append({"role": "user", "content": feed})
    response = openai.ChatCompletion.create(model=model, messages=conversation, temperature=t, max_tokens=64)
    answer = response["choices"][0]['message']['content']
    conversation.append({"role": "assistant", "content": answer})
    return answer

def load_project_description(datafile):
    c = ""
    try:
        with open(datafile, "r") as f:
            c = f.read()
    except FileNotFoundError:
        print("Not such file", PRESENTATION_FILE)
        exit(1)
    return c

def write_to_json(json, question, response):
    content = f"###Human: {question} ###Assistant: {response}"
    line = '{"text": "' + content + '"}\n'
    json.write(line)

def write_to_csv(writer, question, response):
    raw_text = f"###Human:{question}### Assistant:{response}"
    writer.writerow([question, response, raw_text])

def main():
    json = open("woodetect-faq-300.jsonl", 'a')
    woodetect_descr = "Woodetect est le nouvel outil proposé aux organismes souhaitant lutter efficacement contre le trafic de bois. Un réseau de capteurs acoustiques permettra de détecter toutes activités suspectes tels que des camions ou tronçonneuses et alertera en temps réel les autorités sur place. Les organisme disposeront d’un système de surveillance autonome."
    bot_seed = load_project_description(PRESENTATION_FILE)
    bot_seed += "Limite ta réponse à 30 mots."
    bot_seed += "Tu est un chatbot qui repond à des questions sur le projet woodetect de manière amicale. Tes reponses sont très courtes et simple. Ne fait jamais de bullet point.\n"
    qa = ["l'interface utilisateur",#0
          "les cibles",#1
          "un bug du site",#2
          "la sécurité",#3
          "l'installation et déploiement",#4
          "le cout",#5
          "l'écologie",#6
          "le fonctionnement",#7
          "le legal"]#8
    roles_qa_relationship = dict()
    roles_qa_relationship["internaute"] = ["une question con", qa[2], qa[0]] 
    roles_qa_relationship["un garde forestier"] = [qa[0], qa[1], qa[4], qa[5], qa[7], qa[2]]
    roles_qa_relationship["particulier avec une petite foret"] = [qa[4], qa[6], qa[7], qa[2]] 
    roles_qa_relationship["investiseur"]= [qa[1], qa[5], qa[2]] 
    with open('woodetect-faq.csv', 'w', newline='') as c:
        writer = csv.writer(c)
        writer.writerow(['Concept', 'Description', 'Text'])
        for role, aspects in roles_qa_relationship.items():
            print(f"interpreting role : {role}.")
            asker_seed = woodetect_descr
            asker_seed += f"\nTu est un {role}, tu pose une question sur woodetect, tu parle comme {role}. \n"
            asker_seed += "Limite ta question à 10 mots"
            random.shuffle(aspects)
            for aspect in aspects:
                print(f"asking about : {aspect}")
                asker_feed = [{"role": "system", "content": asker_seed}]
                bot_feed = [{"role": "system", "content": bot_seed}]
                for i in range(0, 25):
                    job = f"Tu est {role}, pose une question sur {aspect}."
                    if "bug" in aspect:
                        job += "Tu a rencontré un bug, décrit le bug, précise la page du site internet sur laquelle tu a rencontré le bug."
                    question = get_gpt_answer(job, asker_feed, t=0.9)
                    print(f"asking question : {question}")
                    response = get_gpt_answer(question, bot_feed)
                    print("writing question/response to file...")
                    write_to_json(json, question, response)
                    write_to_csv(writer, question, response)

if __name__ == "__main__":
    main()
