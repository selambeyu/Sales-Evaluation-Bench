from unsloth import FastLanguageModel, is_bfloat16_supported
import os
import torch
from datasets import load_dataset
from trl import ORPOTrainer, ORPOConfig
from transformers import TrainingArguments, TrainerCallback
import logging

# Configuration
MODEL_NAME = "unsloth/Qwen2.5-Coder-7B-Instruct-bnb-4bit" # Recommended backbone
MAX_SEQ_LENGTH = 2048
LORA_RANK = 16
DATA_FILE = "preference_data.jsonl"
OUTPUT_DIR = "tenacious-critic-adapter"
LOG_FILE = "training_run.log"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def train():
    logger.info("Starting Act IV Training Run")
    
    # 1. Load Model and Tokenizer
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=MODEL_NAME,
        max_seq_length=MAX_SEQ_LENGTH,
        load_in_4bit=True,
    )

    # 2. Add LoRA adapters
    model = FastLanguageModel.get_peft_model(
        model,
        r=LORA_RANK,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                        "gate_proj", "up_proj", "down_proj"],
        lora_alpha=16,
        lora_dropout=0,
        bias="none",
        use_gradient_checkpointing="unsloth",
        random_state=3407,
    )

    # 3. Load and Format Dataset
    dataset = load_dataset("json", data_files=DATA_FILE, split="train")

    def format_orpo(example):
        return {
            "prompt": example["prompt"],
            "chosen": example["chosen"],
            "rejected": example["rejected"],
        }

    dataset = dataset.map(format_orpo)
    
    # Split into train/eval for monitoring
    dataset = dataset.train_test_split(test_size=0.1)

    # 4. Define Trainer
    trainer = ORPOTrainer(
        model=model,
        args=ORPOConfig(
            learning_rate=8e-6, # Slightly higher for ORPO
            lr_scheduler_type="cosine",
            max_length=MAX_SEQ_LENGTH,
            max_prompt_length=MAX_SEQ_LENGTH // 2,
            beta=0.1, 
            per_device_train_batch_size=2,
            gradient_accumulation_steps=4,
            max_steps=60, # 30-90 mins wall time target
            fp16=not is_bfloat16_supported(),
            bf16=is_bfloat16_supported(),
            logging_steps=1,
            eval_strategy="steps",
            eval_steps=10,
            optim="paged_adamw_32bit",
            output_dir=OUTPUT_DIR,
            report_to="none", # We log to FileHandler
        ),
        train_dataset=dataset["train"],
        eval_dataset=dataset["test"],
        tokenizer=tokenizer,
    )

    # 5. Train
    logger.info("Hyperparameters: LR=8e-6, BatchSize=8, MaxSteps=60, Beta=0.1")
    train_result = trainer.train()
    
    # Log metrics
    logger.info(f"Training completed. Metrics: {train_result.metrics}")

    # 6. Save Adapter
    model.save_pretrained(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)
    logger.info(f"Model saved to {OUTPUT_DIR}")

if __name__ == "__main__":
    train()
