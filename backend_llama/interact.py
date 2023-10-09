from subprocess import Popen, PIPE, STDOUT

woodetect = """
Woodetect: Outil de surveillance autonome contre le trafic de bois illégal. Utilise un réseau de capteurs acoustiques pour détecter des activités suspectes (camions, tronçonneuses) et alerter les autorités en temps réel.

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

Comment s’installe le capteur ? Le capteur sera fourni avec une notice d’installation mais l’utilisateur à la possibilité de demander une installation par un professionnel.
Comment recevoir les alertes ? Les notifications sont envoyées automatiquement par mail en cas d’alerte et par notification si l’application est installée
Comment est alimenté le capteur ? Le capteur est alimenté par des batteries de 9V rechargeable par le solaire.
Comment sont gérées les données personnelles ? Nous respectons le RGPD et mettons tout en place pour assurer la sécurité des informations personnelles.
Pour toute questions supplémentaires, nous possédons un mail de contact.

contact : contact@woodetect.com
site : https://www.woodetect.com/
tél : 06 03 98 60 75
mail : woodetect_2024@labeip.epitech.eu
"""

def parse_dumb_response(text):
    dumb = ["llama_print_timings", "Bot:", "User:", "[", "Client:"]
    for d in dumb:
        pos = text.find(d)
        if pos != -1:
            text = text[:pos]
    if text == "":
        text = "Je n'ai pas compris votre question."
    return text

def llama_cpp_call(woodetect, instruction, question):
    formatted = f"[INST] Client:{question} [/INST]"
    # Command and parameters as a list
    prompt = f"{woodetect}\n{instruction}\n:{formatted}"
    command = [
        "./llama.cpp/main",
        "-m", "./llama.cpp/ggml-model-q4_0.gguf",
        "--temp", "0.2",
        "--ctx-size", "2048",
        "--frequency-penalty", "1.4",
        "--presence-penalty", "1.4",
        "-p", prompt,
        "-n", "180"
    ]
    print("loading...")
    process = Popen(command, stdout=PIPE, stderr=STDOUT)
    stdout, stderr = process.communicate()
    utf = stdout.decode('utf-8')
    pos_start = utf.find("[/INST]") + len("[/INST]")
    if pos_start != -1:
        utf = utf[pos_start:]
    utf = parse_dumb_response(utf)
    return utf, stderr

instruction = "Conversation entre commercial et un potentiel futur utilisateur. L'utilisateur pose des questions."

while True:
    question = input("User: ")
    out, err = llama_cpp_call(woodetect, instruction, question)
    if err != None:
        print("Error: ", err)
    print(out)