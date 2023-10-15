
from subprocess import Popen, PIPE, STDOUT

def write_log(text):
    with open("log.txt", "a") as f:
        f.write(text + "\n")

def parse_dumb_response(answer):
    # need to be in proper order
    dumb = ["llama_print_timings"]
    surplus = []
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
        text = llama_cpp_call(answer)
    return text

def llama_cpp_call(user_msg):
    prefix = "###Assistant: "
    prompt = f"###Human:{user_msg}\n{prefix}"
    # Command and parameters as a list
    command = [
        "./llama.cpp/main",
        "-m", "../../llama-2-7b.Q8_0.gguf",
        "--lora", "../../woodetect-lora-q8-LATEST.bin",
        "--ctx-size", "2048",
        "-p", prompt,
        "-n", "64"
    ]
    process = Popen(command, stdout=PIPE, stderr=STDOUT)
    stdout, stderr = process.communicate()
    utf = stdout.decode('utf-8')
    pos_start = utf.find(prefix) + len(prefix)
    if pos_start != -1:
        utf = utf[pos_start:]
    utf = parse_dumb_response(utf)
    if "llama" in llm_response:
        print("Fatal error:", llm_response)
        write_log(llm_response)
        llm_response = "A problem occured with the LLM server. Please try again later."
    return utf, stderr