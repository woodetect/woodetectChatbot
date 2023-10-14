from subprocess import Popen, PIPE, STDOUT

woodetect = """
""" # empty if fine-tuned

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

instruction = "" # no need if fine-tuned

while True:
    question = input("User: ")
    out, err = llama_cpp_call(woodetect, instruction, question)
    if err != None:
        print("Error: ", err)
    print(out)