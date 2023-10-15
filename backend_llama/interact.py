import time
from subprocess import Popen, PIPE, STDOUT

from interference_channel import *

control = pyllama()
for word in control.pyllama_next():
    if control.is_loading():
        print("Waiting for llm...")
    if control.pyllama_exited():
        break
    if control.pyllama_wait_input():
        time.sleep(0.6)
        question = input("\nEnter query: ")
        formatted_question = f"###Human: {question}\n###Assistant: "
        control.send(formatted_question)
    print(word, end=' ')
    if '\n' in word:
        print()
        