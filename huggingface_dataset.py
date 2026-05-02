import os
from datasets import load_dataset, DatasetDict
from dotenv import load_dotenv

load_dotenv()

def push_to_huggingface():
    """
    Script to package the tenacious_bench_v0.1 splits and push them to HuggingFace Hub.
    Requires huggingface_hub to be installed and `huggingface-cli login` or HF_TOKEN in .env.
    """
    hf_username = os.getenv("HF_USERNAME")
    hf_token = os.getenv("HF_TOKEN")
    
    if not hf_username:
        print("Error: HF_USERNAME not found in .env file.")
        return

    print("Loading local splits...")
    
    data_files = {
        "train": "tenacious_bench_v0.1/train/data.jsonl",
        "validation": "tenacious_bench_v0.1/dev/data.jsonl",
        "test": "tenacious_bench_v0.1/held_out/data.jsonl"
    }
    
    # Check if files exist before trying to load
    for split, path in data_files.items():
        if not os.path.exists(path):
            print(f"Error: Required partition {path} not found. Run filter_and_split.py first.")
            return

    # Load dataset splits individually to avoid schema inference issues
    dataset_dict = {}
    for split, path in data_files.items():
        print(f"Loading {split} split...")
        dataset_dict[split] = load_dataset("json", data_files=path, split="train")
    
    dataset = DatasetDict(dataset_dict)
    
    # Fix schema mismatch by ensuring prior_thread is always a string (not null)
    def fix_schema(example):
        if example["input"].get("prior_thread") is None:
            example["input"]["prior_thread"] = ""
        return example
    
    print("Standardizing schema...")
    dataset = dataset.map(fix_schema)
    
    hf_repo_name = f"{hf_username}/Tenacious-Bench-v0.1"
    print(f"Dataset loaded successfully. Preparing to push to {hf_repo_name}...")
    
    try:
        dataset.push_to_hub(hf_repo_name, private=False, token=hf_token)
        print(f"Success! Dataset pushed to https://huggingface.co/datasets/{hf_repo_name}")
    except Exception as e:
        print(f"Failed to push dataset to Hub. Error: {e}")

from huggingface_hub import HfApi
import logging

def push_model_to_huggingface():
    """
    Uploads the trained LoRA adapter to HuggingFace Hub.
    """
    hf_username = os.getenv("HF_USERNAME")
    hf_token = os.getenv("HF_TOKEN")
    model_path = "training/tenacious-critic-adapter"
    
    if not os.path.exists(model_path):
        print(f"Error: Model folder not found at {model_path}")
        return

    repo_id = f"{hf_username}/tenacious-critic-adapter"
    print(f"Preparing to push model adapter to {repo_id}...")
    
    api = HfApi()
    try:
        api.create_repo(repo_id=repo_id, repo_type="model", exist_ok=True, token=hf_token)
        api.upload_folder(
            folder_path=model_path,
            repo_id=repo_id,
            repo_type="model",
            token=hf_token,
            ignore_patterns=["checkpoint-*"]
        )
        print(f"Success! Model pushed to https://huggingface.co/{repo_id}")
    except Exception as e:
        print(f"Failed to push model to Hub. Error: {e}")

if __name__ == "__main__":
    print("--- Starting Hugging Face Upload Phase ---")
    push_to_huggingface()
    print("\n--- Starting Model Adapter Upload Phase ---")
    push_model_to_huggingface()
