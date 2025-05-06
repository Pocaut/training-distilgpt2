# This code is for running the model on your own machine
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import torch
import re

model_path = "YOUR_MODEL_PATH"
model = GPT2LMHeadModel.from_pretrained(model_path)
tokenizer = GPT2Tokenizer.from_pretrained(model_path)
model.eval()

if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

special_token_pattern = re.compile(r"<([A-ZÀ-Ú]+)>")

print("Chat with your AI! Type 'exit' to quit.\n")

while True:
    user_input = input("You: ")

    if user_input.lower() in ["exit", "quit"]:
        print("Exiting chat.")
        break

    match = special_token_pattern.search(user_input)
    special_token = match.group(0) if match else ""

    if special_token:
        prompt = f"{special_token} {user_input.replace(special_token, '').strip()}"
    else:
        prompt = user_input.strip()

    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, padding=True).to(model.device)
    input_length = inputs["input_ids"].shape[1] 

    response = ""
    attempts = 0
    max_attempts = 3

    while attempts < max_attempts:
        with torch.no_grad():
            output = model.generate(
                **inputs,
                max_new_tokens=100,
                pad_token_id=tokenizer.eos_token_id,
                do_sample=True,
                temperature=0.9,
                top_p=0.95,
            )

        generated_tokens = output[0][input_length:]
        response = tokenizer.decode(generated_tokens, skip_special_tokens=True).strip()

        # This if() is only necessary because i mistakenly allowed the WhatsApp system message <Mensagem Editada> through the filter. 
        if "<Mensagem editada>" in response:
            print("❌ Bot generated unwanted phrase. Retrying...\n")
            attempts += 1
            continue
        else:
            break

    if special_token:
        response = f"{special_token} {response}"

    print(f"Bot: {response}\n")
