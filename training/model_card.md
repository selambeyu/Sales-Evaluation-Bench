# Model Card: Tenacious Sales Critic v0.1

## Model Details
- **Developer:** Tenacious Consulting Engineering Team
- **Model Type:** LoRA adapter for Qwen2.5-Coder-7B
- **Language:** English
- **License:** CC-BY-4.0
- **Finetuned from model:** `unsloth/Qwen2.5-Coder-7B-Instruct-bnb-4bit`

## Intended Use
- **Primary Use:** Automated rejection sampling for B2B sales outreach emails.
- **Goal:** To detect and flag "Signal Over-Claiming" where an agent asserts higher confidence than the underlying hiring signals support.
- **Out-of-Scope:** General-purpose email writing, legal advice, or medical consultation.

## Training Data
- **Source:** Tenacious-Bench v0.1 Training Partition.
- **Size:** 51 validated (prompt, chosen, rejected) preference pairs.
- **Method:** Rewritten failed historical traces from the Week 10 Conversion Engine.

## Training Procedure
- **Objective:** ORPO (Odds Ratio Preference Optimization).
- **Hyperparameters:**
  - Learning Rate: 8e-6
  - Batch Size: 8 (per-device 2, grad-accum 4)
  - Beta: 0.1
  - Max Steps: 60
  - Optimizer: Paged AdamW 32-bit
- **Hardware:** Google Colab T4 (16GB VRAM).

## Evaluation Results
- **Delta A (vs. Week 10 Baseline):** +6.5% lift in brand safety pass rate (CI: [0.0, 16.1%]).
- **Delta B (vs. Prompt-Eng):** +9.7% lift (ORPO training outperformed pure prompt engineering).
- **Delta C (vs. Legacy Tau):** +42.0% improvement over Week 10 retail baselines.
- **Inference Latency:** ~85ms additional overhead per email (Cost-Pareto Efficient).

## Ethical Considerations
- The model is trained to increase honesty and grounding in sales outreach. 
- It reduces the risk of "Tone Drift" and "Condescension" which protects the brand reputation of the sender.

## Limitations
- Performance may degrade on niche industries not represented in the training set (e.g., highly technical biotech).
- Relies on the quality of the input signal brief; "garbage in, garbage out" applies to the critic as well.
