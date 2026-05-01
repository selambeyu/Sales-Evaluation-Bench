# Sales Agent Evaluation Bench (Tenacious-Bench v0.1)

This repository contains the complete 10-step evaluation and training pipeline for the Tenacious B2B Sales Conversational Agent. It includes the generation scripts to build a 250-task evaluation dataset, an LLM-as-a-judge scoring evaluator, and a HuggingFace TRL script to preference-tune a LoRA critic model to reject "Signal Over-Claiming".

## Current Status
- **What is working:** The Tenacious-Bench dataset generation pipeline is fully operational. We have successfully authored 250 tasks using a four-pronged synthesis approach and filtered them via our LLM-as-a-judge (`scoring_evaluator.py`). The dataset is partitioned into train (50%), dev (30%), and held-out (20%) with zero contamination.
- **What is blocked:** We are currently awaiting sufficient compute allocation to complete the Qwen2.5-0.5B LoRA preference-tuning run.

## Forward Plan
- **Day 4:** Finalize the preference-tuning dataset formatting (`prepare_preference_data.py`) and read the path-specific literature (Path B: SimPO/ORPO).
- **Day 5:** Execute the LoRA training run on Google Colab or RunPod, targeting a 30-60 minute wall time.
- **Day 6:** Run the ablation evaluations (Delta A and Delta B) against the sealed held-out partition and log the results.
- **Day 7:** Ship the final artifacts: publish the HuggingFace dataset and model adapter, write the technical blog post, and engage with the open-source community.

## Repository Structure
- `audit_memo.md` & `failure_taxonomy.md`: Analysis of the Week 10 traces identifying Signal Over-Claiming as the critical brand risk.
- `schema.json`: The task and rubric definition based on the Tenacious Style Guide.
- `generation_scripts/`: Scripts to synthesize, programmatically generate, and extract 250 tasks, then split them into 50/30/20 train/dev/held_out partitions.
- `scoring_evaluator.py`: OpenRouter LLM-as-a-judge that enforces the 5 Tone Markers.
- `contamination_check.py`: Mathematically proves zero 8-gram leakage between train and held-out sets.
- `training/`: Contains `prepare_preference_data.py` and `train_lora_judge.py` to train a Qwen2.5-0.5B ORPO critic.
- `eval_pipeline.py`: Runs the ablation between baseline and trained model.
- `huggingface_dataset.py`: Packaging script.
- `blog_post.md` & `executive_memo.md`: Final deliverables and deployment recommendation.

## Setup & Reproducibility

We use `uv` for lightning-fast Python dependency management.

```bash
# 1. Initialize the environment
uv sync

# 2. Add dependencies
uv add openai pydantic python-dotenv datasets transformers peft trl torch

# 3. Set your OpenRouter API Key
cp .env.example .env
# Edit .env and insert your OPENROUTER_API_KEY
```

## Running the Pipeline

### 1. Dataset Generation
```bash
uv run python generation_scripts/extract_traces.py
uv run python generation_scripts/programmatic_tasks.py
uv run python generation_scripts/synthesize_tasks.py --count 60
# (Ensure data/hand_authored_tasks.jsonl is populated)

uv run python generation_scripts/filter_and_split.py
uv run python contamination_check.py
```

### 2. Training (Path B: Judge Model)
```bash
uv run python training/prepare_preference_data.py
uv run python training/train_lora_judge.py
```

### 3. Evaluation & Ablations
```bash
uv run python eval_pipeline.py
```

*See `ablation_results.json` for the Delta A / Delta B metrics.*
