import discord
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import torch
import re

# Load finetuned model.
model_path = "YOUR_MODEL_PATH"
model = GPT2LMHeadModel.from_pretrained(model_path)
tokenizer = GPT2Tokenizer.from_pretrained(model_path)
model.eval()

# Set pad token if missing.
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

# Set up Discord client.
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

BOT_TOKEN = "BOT_DISCORD_TOKEN"

# Regex to extract special token (e.g., <PEDRO>)
# In my use-case the special token is meant to teach the AI to speak as someone from the groupchat.
special_token_pattern = re.compile(r"<([A-ZÀ-Ú]+)>")

# Define unwanted phrases to avoid
# This specific phrase managed to go through the formatting filter. Unprofessionaly, i'm filtering it now.
unwanted_phrases = ["<Mensagem editada>"]

@client.event
async def on_ready():
    print(f"✅ Logged in as {client.user}")

@client.event
async def on_message(message):
    # Ignore bot's own messages
    if message.author == client.user:
        return

    # Check if bot is mentioned or starts with !bl (My chosen command)
    bot_mentioned = client.user in message.mentions
    starts_with_bl = message.content.strip().lower().startswith("!bl")

    if not (bot_mentioned or starts_with_bl):
        return  # Ignore all other messages

    # Extract message content (remove command or mention)
    user_input = message.content

    if bot_mentioned:
        user_input = user_input.replace(f"<@{client.user.id}>", "").strip()

    if starts_with_bl:
        user_input = user_input[3:].strip()  # Remove "!bl"

    # Detect special token (like <PEDRO>)
    match = special_token_pattern.search(user_input)
    special_token = match.group(0) if match else ""

    # Prepare input for model
    prompt = user_input
    if special_token:
        prompt = special_token + " " + user_input.replace(special_token, "").strip()

    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, padding=True).to(model.device)
    input_length = inputs["input_ids"].shape[1]

    # Retry logic for unwanted phrases
    # I added this specifically because some <Message Edited> tags weren't filtered in the formatAndParse file
    # Not needed if you do the formatting right
    response = ""
    attempts = 0
    max_attempts = 3

    while attempts < max_attempts:
        with torch.no_grad():
            output = model.generate(
                **inputs,
                max_new_tokens=25,  # Response length
                pad_token_id=tokenizer.eos_token_id,
                do_sample=True,
                temperature=0.6, # Context Randomness
                top_p=0.85, # Randomness
                repetition_penalty=1.2, # Stops AI from repeating a word or phrase too much
                early_stopping=True,
            )

        # Slice the generated response to exclude the prompt
        generated_tokens = output[0][input_length:]
        response = tokenizer.decode(generated_tokens, skip_special_tokens=True).strip()

        # Retry if unwanted phrases are in response
        if any(phrase in response for phrase in unwanted_phrases):
            print("Bot generated unwanted phrase. Retrying...\n")
            attempts += 1
            continue
        else:
            break

    # If special token is used, prepend it
    if special_token:
        response = f"{special_token} {response}"

    # Sanitize response if unwanted phrase if found.
    for phrase in unwanted_phrases:
        response = response.replace(phrase, "")

    # Ensure response is not empty
    if not response.strip():
        response = "Sorry, i couldn't understand that."

    await message.channel.send(response)

client.run(BOT_TOKEN)
