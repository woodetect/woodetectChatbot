## model Formats

- Lora : folder with adapter_model.bin the file that converted to ggml
- ggml : bin file, usually named ggml-adapter-model.bin
- gguf : file that end with gguf, used to store quantified base model

## Model source

Thebloke on huggingface seem good

7B GGUF downloadlink for wget
https://huggingface.co/TheBloke/Llama-2-7B-GGUF/blob/main/llama-2-7b.Q4_0.gguf

## llama.cpp

usefull: https://rentry.org/cpu-lora

**Compile :**

sudo apt install build-essentials

mkdir .\llama.cpp\build

cd .\llama.cpp\build

# compile with GPU, remove CUBLAS for only CPU
cmake .. -A x64 -DLLAMA_CUBLAS=ON

cmake --build . --config Release

**Finetune :**

`./finetune --model-base ../saved_models/llama-q4_0.gguf --checkpoint-in  chk-lora-llama-2-7b-q8_0-wood-LATEST.gguf --checkpoint-out chk-lora-llama-2-7b-q8_0-wood-ITERATION.gguf --lora-out lora-llama-2-7b-q8_0-wood-ITERATION.bin --train-data "woodetect.txt" --save-every 20 --threads 20 --adam-iter 1125 --batch 4 --ctx 256 --use-checkpointing`

recent commit seem to cause ABORT see https://github.com/ggerganov/llama.cpp/issues/3578
tmp fix:
git checkout a03ce38455544121c5c00cf845def1443acd6ac8

### IMPORTANT :

/!\ Convert epoch's to adam-iter : (epochs * training samples) / batch size

epochs = (adam_iter*batch_size) / training_samples

/!\ Training will stop when --adam-iter is reached OR --epochs is reached (if --epochs is set). If you don't set --adam-iter to a large enough number when using --epochs, training could stop much earlier than you expect.

/!\ about --ctx : A context size smaller than the base model shouldn't affect the base model too much, but each of your training data sections should be under this context size, or they will be cut off at the context size.

**Convert :**

python3 convertors/convert-lora-to-ggml.py saved_models/finetunedModel

**Interference :**

`./llama.cpp/build/bin/main \   -m ./saved_models/llama-q4_0.gguf --lora ./saved_models/llamawood2/ggml-adapter-model.bin \   --prompt "###Human: comment marche woodetect ? ###Assistant:"`

MODEL OUTPUT GARGAGE LIKE BASE MODEL

### debug process

try actual merging :
https://rentry.org/llama-cpp-conversions#merging-loras-into-a-model
DIDNT WORK

try to stop using q4 and use q8 might fix ?
WORKING --> PROBLEM WAS FINETUNING ON Q4_0!!!

llama.cpp can use RAM instead of VRAM possible to finetune on desktop 
FINETUNE WORKED

## Autotrain

**Finetune :**

`autotrain llm --train --project_name llamawood --model meta-llama/Llama-2-7b-hf --data_path ./data --use_peft --use_int4 --learning_rate 2e-4 --train_batch_size 4 --num_train_epochs 9 --trainer sft > training.log &`

then get output folder that is in HF format

**Convert :**

`python3 convert-lora-to-ggml.py saved_models/llamawood`

NO ERROR DURING CONVERSION 

**Execute interference**

./llama.cpp/build/bin/main -m ./saved_models/ggml-model-q4_0.gguf --lora ./saved_models/llamawood/ggml-adapter-model.bin --prompt "###Human: Comment sont installer les capteurs ? ### Assistant: " --temp 0
"""

MODEL OUTPUT GARBAGE

### debug process so far

it appear finetuning with autotrain  wasn't done properly
second run destroyed first run at 500 epoch with good curve
maybe try again

## Finetuner2.py

**Finetune :**

script from some reddit user is working :

https://pastebin.com/vPX76tNi

script use transformers libraries with AutoModelForCausalLM

Error happen during conversion : `Error: unrecognized tensor base_model.model.lm_head.lora_A.weight` but ggml file (.bin) is still generated ?

**interference :**

`./llama.cpp/build/bin/main   -m ./saved_models/llama-q4_0.gguf --lora ./saved_models/llamawood150/ggml-adapter-model.bin --prompt "###Human: comment marche woodetect ? ###Assistant: woodetect permet de lutter contre" --temp 0`

MODEL OUTPUT GARGAGE LIKE BASE MODEL

### debug process

no solution found yet