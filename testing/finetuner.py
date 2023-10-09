"""
NEED TO BE RUN ON VAST.AI, OUT OF MEMORY ON M1 MAC

NOT WORKING, JSONL DATASET FORMAT PROBLEM
"""
import argparse
import bitsandbytes as bnb
from datasets import load_dataset
from functools import partial
import os
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training, AutoPeftModelForCausalLM
import torch
from peft import LoraConfig
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    Trainer,
    TrainingArguments,
    BitsAndBytesConfig,
    DataCollatorForLanguageModeling,
    AutoTokenizer,
    TrainingArguments,
    TrainerCallback,
)
from datasets import load_dataset

SAVE_MODEL_PATH = 'finetuned/'
DATASET_PATH = './data/woodetect-faq.jsonl'
MODEL_NAME = "meta-llama/Llama-2-7b-hf" 
#MODEL_NAME = "./llama_hf" 

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

def load_model(model_name: str, bnb_config: dict) -> tuple:
    """
    Loads a pre-trained model and tokenizer for fine-tuning.

    Args:
        model_name (str): The name of the pre-trained model to load.
        bnb_config (dict): The quantization configuration for the model.

    Returns:
        tuple: A tuple containing the loaded model and tokenizer.
    """
    n_gpus = torch.cuda.device_count()
    max_memory = f'{16000}MB'
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        quantization_config=bnb_config,
        device_map="auto", # dispatch efficiently the model on the available ressources
        max_memory = {i: max_memory for i in range(n_gpus)},
    )
    tokenizer = AutoTokenizer.from_pretrained(model_name, use_auth_token=True)
    # Needed for LLaMA tokenizer
    tokenizer.pad_token = tokenizer.eos_token
    return model, tokenizer

def create_bnb_config():
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
    )
    return bnb_config

def create_peft_config(modules):
    """
    Create Parameter-Efficient Fine-Tuning config for your model
    :param modules: Names of the modules to apply Lora to
    """
    config = LoraConfig(
        r=16,  # dimension of the updated matrices
        lora_alpha=64,  # parameter for scaling
        target_modules=modules,
        lora_dropout=0.1,  # dropout probability for layers
        bias="none",
        task_type="CAUSAL_LM",
    )
    return config

def find_all_linear_names(model):
    cls = bnb.nn.Linear4bit #if args.bits == 4 else (bnb.nn.Linear8bitLt if args.bits == 8 else torch.nn.Linear)
    lora_module_names = set()
    for name, module in model.named_modules():
        if isinstance(module, cls):
            names = name.split('.')
            lora_module_names.add(names[0] if len(names) == 1 else names[-1])

    if 'lm_head' in lora_module_names:  # needed for 16-bit
        lora_module_names.remove('lm_head')
    return list(lora_module_names)

def print_trainable_parameters(model, use_4bit=False):
    """
    Prints the number of trainable parameters in the model.
    """
    trainable_params = 0
    all_param = 0
    for _, param in model.named_parameters():
        num_params = param.numel()
        # if using DS Zero 3 and the weights are initialized empty
        if num_params == 0 and hasattr(param, "ds_numel"):
            num_params = param.ds_numel
        all_param += num_params
        if param.requires_grad:
            trainable_params += num_params
    if use_4bit:
        trainable_params /= 2
    print(
        f"all params: {all_param:,d} || trainable params: {trainable_params:,d} || trainable%: {100 * trainable_params / all_param}"
    )

class PeftSavingCallback(TrainerCallback):
    def on_save(self, args, state, control, **kwargs):
        checkpoint_path = os.path.join(args.output_dir, f"checkpoint-{state.global_step}")
        kwargs["model"].save_pretrained(checkpoint_path)
        print(f"saving checkpoint at {checkpoint_path}")

def train(model, tokenizer, dataset, output_dir):
    # Apply preprocessing to the model to prepare it by
    # 1 - Enabling gradient checkpointing to reduce memory usage during fine-tuning
    model.gradient_checkpointing_enable()
    # 2 - Using the prepare_model_for_kbit_training method from PEFT
    model = prepare_model_for_kbit_training(model)
    # Get lora module names
    modules = find_all_linear_names(model)
    # Create PEFT config for these modules and wrap the model to PEFT
    peft_config = create_peft_config(modules)
    model = get_peft_model(model, peft_config)
    # Print information about the percentage of trainable parameters
    print_trainable_parameters(model)
    # Training parameters
    trainer = Trainer(
        model=model,
        train_dataset=dataset,
        args=TrainingArguments(
            per_device_train_batch_size=8,
            gradient_accumulation_steps=4,
            warmup_steps=2,
            max_steps=20,
            learning_rate=2e-4,
            fp16=True,
            logging_steps=1,
            output_dir="./results",
            optim="paged_adamw_8bit",
        ),
        data_collator=DataCollatorForLanguageModeling(tokenizer, mlm=False)
    )
    model.config.use_cache = False  # re-enable for inference to speed up predictions for similar inputs
    ### SOURCE https://github.com/artidoro/qlora/blob/main/qlora.py
    # Verifying the datatypes before training
    dtypes = {}
    for _, p in model.named_parameters():
        dtype = p.dtype
        if dtype not in dtypes: dtypes[dtype] = 0
        dtypes[dtype] += p.numel()
    total = 0
    for k, v in dtypes.items(): total+= v
    for k, v in dtypes.items():
        print(k, v, v/total)
    do_train = True
    # Launch training
    print("Training...")
    if do_train:
        train_result = trainer.train()
        metrics = train_result.metrics
        trainer.log_metrics("train", metrics)
        trainer.save_metrics("train", metrics)
        trainer.save_state()
        print(metrics)    
    # Saving model
    print("Saving last checkpoint of the model...")
    os.makedirs(output_dir, exist_ok=True)
    trainer.model.save_pretrained(output_dir)
    # Free memory for merging weights
    del model
    del trainer
    torch.cuda.empty_cache()

bnb_config = create_bnb_config()
model, tokenizer = load_model(MODEL_NAME, bnb_config)
dataset = load_dataset('json', data_files=DATASET_PATH, split='train')
data = dataset.shuffle(seed=23456).remove_columns("text")
## Preprocess dataset
output_dir = "results/llama2/final_checkpoint"
train(model, tokenizer, dataset, output_dir)
print("training finished!")
model = AutoPeftModelForCausalLM.from_pretrained(output_dir, device_map="auto", torch_dtype=torch.bfloat16)
model = model.merge_and_unload()
os.makedirs(SAVE_MODEL_PATH, exist_ok=True)
model.save_pretrained(SAVE_MODEL_PATH, safe_serialization=True)
# save tokenizer for easy inference
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
tokenizer.save_pretrained(SAVE_MODEL_PATH)
