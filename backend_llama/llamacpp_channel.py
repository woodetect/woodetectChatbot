
from subprocess import Popen, PIPE, STDOUT, DEVNULL
import select
import threading

class pyllamacpp:
    # TODO : change stop_keyword and ctx / n-predict later
    def __init__(self, stop_keyword="."):
        self.lock = threading.Lock()
        command = [
            "../llama.cpp/bin/main",
            "-m", "../saved_models/llama-2-7b-q4_0.gguf",
            "--interactive-first",
            "--reverse-prompt", stop_keyword, 
            "--presence-penalty", "1.0",
            "--frequency-penalty", "1.0",
            "--ctx-size", "128",
            "--n-predict", "128"
        ]
        self.exit_request = False
        self.wait_input = False
        self.generation_started = False
        self.stop_keyword = stop_keyword
        self.process = Popen(command,
                             stdout=PIPE,
                             stderr=PIPE,
                             stdin=PIPE,
                             bufsize=1,
                             universal_newlines=True)
        self.phrase = ""
        self.phrase_history = []

    def write_log(self, text):
        with open("log.txt", "a") as f:
            f.write(text + "\n")
    
    def is_loading(self):
        return not self.generation_started

    def send(self, text):
        self.phrase = ""
        self.phrase_history.append(self.phrase)
        with self.lock:
            print("pyllamacpp: sending message to llm: " + text)
            try:
                self.process.stdin.write(text)
                self.process.stdin.flush()
            except Exception as e:
                print("pyllamacpp: error sending message to llm.")
    
    def exited(self) -> bool:
        return self.exit_request
    
    def generation_has_started(self) -> bool:
        return self.generation_started
    
    def waiting(self) -> bool:
        return self.wait_input
    
    def get_sentence(self) -> str:
        return self.phrase
    
    def get_sentences_history(self) -> any:
        return self.phrase_history
    
    def get_last_sentence(self) -> str:
        return self.phrase
    
    def next_word(self, verbose=True) -> None:
        timeout = 1.0
        partial_word = ""
        partial_err = ""
        rlist = None
        i = 0
        while True:
            i += 1
            rlist, _, _ = select.select([self.process.stdout, self.process.stderr], [], [], timeout)
            output_char = ""
            err_char = ""
            for readable in rlist:
                if readable is self.process.stdout:
                    output_char = self.process.stdout.read(1)
                elif readable is self.process.stderr:
                    err_char = self.process.stderr.read(1)
            if err_char == '' and self.process.poll() is not None:
                print("\npyllamacpp: process ended.")
                break
            if verbose:
                print(err_char, end='', flush=True)
                print(output_char, end='', flush=True)
            if output_char != '' and self.generation_started == False:
                print("\npyllamacpp: generation started.")
                self.generation_started = True
            elif output_char != '':
                self.wait_input = False
            if err_char == '' and output_char == '':
                self.wait_input = True
                yield ""
            if self.generation_started == False:
                continue
            partial_word += output_char
            partial_err += err_char
            # end log message, mean generation ended
            if self.generation_started == True and err_char != '':
                print("\npyllamacpp: word generation terminated, llm shutdown.")
                break
            if output_char != ' ' and output_char != '\n' and output_char != '\t':
                continue
            if self.stop_keyword in partial_word:
                self.wait_input = True
                yield ""
            returned_word = partial_word
            self.phrase += returned_word
            partial_word = ""
            yield returned_word
        print("\npyllamacpp: process ended.")
        self.exit_request = True
        yield "EXIT"
