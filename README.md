# Sales Agent Evaluation Bench (Tenacious-Bench v0.1)

This repository contains the complete 10-step evaluation and training pipeline for the Tenacious B2B Sales Conversational Agent. It includes the generation scripts to build a 250-task evaluation dataset, an LLM-as-a-judge scoring evaluator, and a HuggingFace TRL script to preference-tune a LoRA critic model to reject "Signal Over-Claiming".

## Current Status (Act III Complete)
- **Dataset (Tenacious-Bench v0.1):** 250 tasks across 4 authoring modes (Trace-derived, Programmatic, Multi-LLM, Hand-authored).
- **Audit Memo:** 600-word audit citing 3 specific Week 10 trace IDs (`trace_id_8f3a2`, `trace_id_9b1c4`, `trace_id_2c4d5`).
- **Path Selection:** Path B (Preference-Tuned Judge) selected and justified in `methodology_rationale.md`.
- **Training Data:** `preference_data.jsonl` generated with 50+ validated (chosen, rejected) pairs using local Qwen/Ollama pipeline.
- **Datasheet:** Completed Gebru + Pushkarna layers.
- **Inter-Rater Agreement:** >80% agreement verified across all 5 tone markers.

## Forward Plan (Act IV: Train, Ablate, Measure)
1. **Training:** Execute the ORPO/SimPO training run on Google Colab T4 using Unsloth.
2. **Ablation (Delta A):** Compare the trained adapter against the Week 10 baseline on the sealed held-out partition.
3. **Ablation (Delta B):** Compare the trained adapter against a prompt-engineered baseline.
4. **Final Deliverables:** Compile the executive memo, blog post, and community engagement artifact.

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
