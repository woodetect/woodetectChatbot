from transformers import AutoModelForCausalLM, AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("tiiuae/falcon-7b-instruct")
model = AutoModelForCausalLM.from_pretrained("tiiuae/falcon-7b-instruct")

inputs = tokenizer("What's the best way to divide a pizza between three people?", return_tensors="pt")
outputs = model.generate(**inputs, max_length=50)