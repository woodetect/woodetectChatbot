import time
from subprocess import Popen, PIPE, STDOUT

from llamacpp_channel import *

control = pyllamacpp()
for word in control.pyllamacpp_next():
    if control.is_loading():
        print("Waiting for llm...")
    if control.pyllamacpp_exited():
        break
    if control.pyllamacpp_wait_input():
        time.sleep(0.3)
        question = input("\nEnter query: ")
        formatted_question = f"###Human: {question}\n###Assistant: "
        control.send(formatted_question)
    print(word, end=' ')
    if '\n' in word:
        print()
        