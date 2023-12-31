
from subprocess import Popen, PIPE, STDOUT, DEVNULL
import select

class pyllamacpp:
    def __init__(self, stop_keyword="###", n_predict="128", ctx_size="512"):
        command = [
            "../llama.cpp/bin/main",
            "-m", "../saved_models/llama-2-7b-q4_0.gguf",
            "--interactive-first",
            "--n-predict", n_predict,
            "--ctx-size", ctx_size,
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
        self.word_history = []

    def write_log(self, text):
        with open("log.txt", "a") as f:
            f.write(text + "\n")
    
    def is_loading(self):
        return not self.generation_started

    def send(self, text):
        self.process.stdin.write(text)
        self.process.stdin.flush()
    
    def pyllamacpp_exited(self) -> bool:
        return self.exit_request
    
    def generation_has_started(self) -> bool:
        return self.generation_started
    
    def pyllamacpp_wait_input(self) -> bool:
        if self.wait_input:
            self.wait_input = False
            return True
        return False
    
    def pyllamacpp_next(self) -> None:
        timeout = 1.0
        partial_word = ""
        partial_err = ""
        rlist = None
        while True:
            rlist, _, _ = select.select([self.process.stdout, self.process.stderr], [], [], timeout)
            output_char = ""
            err_char = ""
            for readable in rlist:
                if readable is self.process.stdout:
                    output_char = self.process.stdout.read(1)
                elif readable is self.process.stderr:
                    err_char = self.process.stderr.read(1)
            #print(f"out ({output_char}) err ({err_char})")
            if err_char == '' and self.process.poll() is not None:
                print("\npyllamacpp: process ended.")
                break
            if err_char == '' and output_char == '':
                self.wait_input = True
                yield ""
            partial_word += output_char
            partial_err += err_char
            print(err_char, end='', flush=True)
            if output_char != '' and self.generation_started == False:
                print("\npyllamacpp: generation started.")
                self.generation_started = True
            if self.generation_started == False:
                continue
            # end log message, mean generation ended
            if self.generation_started == True and err_char != '':
                print("\npyllamacpp: word generation terminated, llm shutdown.")
                break
            if output_char != ' ' and output_char != '\n' and output_char != '\t':
                continue
            if self.stop_keyword in partial_word:
                self.wait_input = True
                yield "STOP"
            returned_word = partial_word
            partial_word = ""
            yield returned_word
        if partial_word:
            yield partial_word
        print("\npyllamacpp: process ended.")
        self.exit_request = True
        yield "EXIT"
