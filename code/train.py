# This is the training algorithm. Took me about 6hrs on 89K groupchat messages. About 248K iterations.
import json
from transformers import GPT2LMHeadModel, GPT2Tokenizer, Trainer, TrainingArguments
from transformers import DataCollatorForLanguageModeling
from torch.utils.data import Dataset
import torch

# Wrapped the whole thing in a Try so i could find any exceptions without the command prompt closing.
try:
    # Step 1: Load the parsed data
    with open('YOUR_PARSED_DATA_PATH', 'r', encoding='utf-8') as f:
        chat_data = json.load(f)

    # Step 2: Tokenizer setup.
    # Using Distilgpt2 since i have a Laptop 3050, bigger model would strain my GPU too much.
    tokenizer = GPT2Tokenizer.from_pretrained("distilgpt2")
    tokenizer.pad_token = tokenizer.eos_token

    # Step 3: Add remetente names as special tokens.
    # Note: I only did this to test if i could make the LLM speak as a specific person, problem is my dataset was too small.
    speakers = list(set(f"<{entry['remetente'].upper()}>" for entry in chat_data if 'remetente' in entry))
    special_tokens = {"additional_special_tokens": speakers}
    tokenizer.add_special_tokens(special_tokens)

    # Step 4: Format messages with and without special speaker tokens.
    messages = []
    for entry in chat_data:
        if "mensagem" in entry and isinstance(entry["mensagem"], str):
            speaker_token = f"<{entry['remetente'].upper()}>"
            mensagem = entry["mensagem"]
            messages.append(f"{speaker_token} {mensagem}")
            messages.append(mensagem)

    if not messages:
        raise ValueError("No valid messages found in the dataset.")

    # Step 5: Tokenize all messages
    class ChatDataset(Dataset):
        def __init__(self, texts, tokenizer):
            self.tokenizer = tokenizer
            self.examples = tokenizer(
                texts,
                padding="max_length",
                truncation=True,
                max_length=128,
                return_tensors="pt"
            )["input_ids"]

        def __len__(self):
            return len(self.examples)

        def __getitem__(self, idx):
            return {"input_ids": self.examples[idx], "labels": self.examples[idx]}

    dataset = ChatDataset(messages, tokenizer)

    # Step 6: Load model and resize token embeddings
    model = GPT2LMHeadModel.from_pretrained("distilgpt2")
    model.resize_token_embeddings(len(tokenizer))

    # Step 7: Training arguments
    training_args = TrainingArguments(
        output_dir="DESIRED_OUTPUT_PATH",
        num_train_epochs=3,
        per_device_train_batch_size=2,
        save_steps=500,
        save_total_limit=2,
        logging_dir="LOGS_PATH",
    )

    # Step 8: Data collator
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False
    )

    # Step 9: Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
        data_collator=data_collator,
    )

    # Step 10: Finetune the model
    trainer.train()

    # Step 11: Save the finetuned model
    model.save_pretrained("DESIRED_FINETUNED_PATH")
    tokenizer.save_pretrained("DESIRED_FINETUNED_PATH")

    print("✅ Model training complete and saved.")

# e tells me where the exception was. Had this trigger only once.
except Exception as e:
    print(f"❌ An error occurred: {e}")
    input("\nPressione Enter para sair...")
