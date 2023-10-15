from subprocess import Popen, PIPE, STDOUT

from interference_channel import *

while True:
    question = input("User: ")
    out, err = llama_cpp_call(question)
    if err != None:
        print("Error: ", err)
    print("AI:", out)