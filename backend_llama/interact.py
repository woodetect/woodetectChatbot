from subprocess import Popen, PIPE, STDOUT

from interference_channel import *

control = pyllama()
for word in control.pyllama_next():
    if control.pyllama_exited():
        break
    if control.pyllama_wait_input():
        question = input("\nEnter query: ")
        formatted_question = f"###Human: {question}\n###Assistant:"
        control.send(formatted_question)
    print(word, end=' ')
    if '\n' in word:
        print()
        