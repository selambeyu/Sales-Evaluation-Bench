import os
import torch
from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments
from peft import LoraConfig, get_peft_model
from trl import ORPOTrainer, ORPOConfig

# Model Configuration
MODEL_ID = "Qwen/Qwen2.5-0.5B"  # Lightweight model to ensure < 90 min training on standard hardware
OUTPUT_DIR = "../models/tenacious-judge-lora"

def train():
    print("Loading dataset...")
    data_path = "../tenacious_bench_v0.1/train/preference_data.jsonl"
    if not os.path.exists(data_path):
        print(f"Data file not found: {data_path}")
        return
        
    dataset = load_dataset("json", data_files=data_path, split="train")

    print(f"Loading {MODEL_ID}...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    tokenizer.pad_token = tokenizer.eos_token
    
    # Load model in bfloat16 if supported, else float16
    dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
    
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        torch_dtype=dtype,
        device_map="auto"
    )

    # Apply LoRA adapter
    print("Applying LoRA...")
    lora_config = LoraConfig(
        r=16,
        lora_alpha=32,
        target_modules=["q_proj", "v_proj"], # Target attention layers
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM"
    )
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    # ORPO Configuration
    orpo_config = ORPOConfig(
        output_dir=OUTPUT_DIR,
        learning_rate=1e-4,
        lr_scheduler_type="linear",
        max_length=1024,
        max_prompt_length=512,
        beta=0.1, # ORPO specific beta parameter
        per_device_train_batch_size=2,
        gradient_accumulation_steps=4,
        optim="adamw_torch",
        num_train_epochs=3,
        logging_steps=10,
        save_strategy="epoch",
        report_to="none" # Disable wandb for local script
    )

    trainer = ORPOTrainer(
        model=model,
        args=orpo_config,
        train_dataset=dataset,
        tokenizer=tokenizer,
    )

    print("Starting ORPO training...")
    trainer.train()

    print(f"Saving final model to {OUTPUT_DIR}...")
    trainer.save_model(f"{OUTPUT_DIR}/final")
    tokenizer.save_pretrained(f"{OUTPUT_DIR}/final")
    print("Training complete!")

if __name__ == "__main__":
    train()
