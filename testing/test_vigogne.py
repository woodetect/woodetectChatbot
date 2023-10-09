
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, GenerationConfig
from vigogne.preprocess import generate_inference_chat_prompt

base_model_name_or_path = "bofenghuang/vigogne-7b-chat"

tokenizer = AutoTokenizer.from_pretrained(base_model_name_or_path, padding_side="right", use_fast=False)
# tokenizer.pad_token = tokenizer.eos_token

model = AutoModelForCausalLM.from_pretrained(
    base_model_name_or_path,
    torch_dtype=torch.float16,
    device_map="auto",
    # load_in_8bit=True,
    # trust_remote_code=True,
    # low_cpu_mem_usage=True,
)

# lora_model_name_or_path = ""
# model = PeftModel.from_pretrained(model, lora_model_name_or_path)

model.eval()

if torch.__version__ >= "2":
    model = torch.compile(model)

def infer(
    user_querys,
    temperature=0.1,
    max_new_tokens=512,
    **kwargs,
):
    prompt = generate_inference_chat_prompt(user_querys, tokenizer=tokenizer)
    input_ids = tokenizer(prompt, return_tensors="pt")["input_ids"].to(model.device)
    input_length = input_ids.shape[1]

    generated_outputs = model.generate(
        input_ids=input_ids,
        generation_config=GenerationConfig(
            temperature=temperature,
            do_sample=temperature > 0.0,
            max_new_tokens=max_new_tokens,
            **kwargs,
          ),
        return_dict_in_generate=True,
    )
    generated_tokens = generated_outputs.sequences[0, input_length:]
    generated_text = tokenizer.decode(generated_tokens, skip_special_tokens=True)
    return generated_text

def chat(**kwargs):
    history = []
    while True:
        user_input = input(">> <|UTILISATEUR|>: ")
        model_response = infer([*history, [user_input, ""]], **kwargs)

        history.append([user_input, model_response])
        print(f">> <|ASSISTANT|>: {history[-1][1]}")
