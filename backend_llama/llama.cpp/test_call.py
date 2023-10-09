from subprocess import Popen, PIPE, STDOUT

woodetect = """
Woodetect utilise des capteurs acoustiques pour détecter des activités suspectes liées au trafic de bois (comme camions ou tronçonneuses) et alerte les autorités en temps réel. Le système est autonome.
"""

def llama_cpp_call(woodetect, instruction, question):
    # Command and parameters as a list
    seed = f"{woodetect}\n{instruction}\nUser: {question}\nBot:"
    print(len(seed))
    command = [
        "./main",
        "-m", "ggml-model-q4_0.gguf",
        "--temp", "0.2",
        "--frequency-penalty", "1.9",
        "--presence-penalty", "1.2",
        "-p", seed,
        "-n", "128"
    ]
    print("loading...")
    process = Popen(command, stdout=PIPE, stderr=STDOUT)
    stdout, stderr = process.communicate()
    utf = stdout.decode('utf-8')
    pos_start = utf.find("Bot:")
    out = utf
    if pos_start != -1:
        out = utf[pos_start:]
    pos_end = out.find("User:")
    if pos_end != -1:
        out = out[:pos_end]
    pos_end = out.find("[end of text]")
    if pos_end != -1:
        out = out[:pos_end]
    pos_end = out.find("llama_print_timings:")
    if pos_end != -1:
        out = out[:pos_end]
    return out, stderr

instruction = "This is a conversation of a chatbot with a customer. The customer is asking about woodetect."

while True:
    question = input("User: ")
    out, err = llama_cpp_call(woodetect, instruction, question)
    if err != None:
        print("Error: ", err)
    print(out)