---
language:
- en
license: cc-by-4.0
tags:
- sales
- evaluation
- lora
- orpo
- qwen
datasets:
- your_username/Tenacious-Bench-v0.1
---

# Model Card: Tenacious-Judge-LoRA

## Model Description
Tenacious-Judge-LoRA is a lightweight critic model fine-tuned using ORPO (Odds Ratio Preference Optimization) to evaluate B2B conversational sales outreach. It acts as a rejection sampling filter to catch "Signal Over-Claiming" and violations of the Tenacious Style Guide before emails are sent to prospects.

- **Base Model:** `Qwen/Qwen2.5-0.5B`
- **Fine-Tuning Method:** LoRA + ORPO
- **Training Data:** `Tenacious-Bench-v0.1` (125 preference pairs)

## Intended Use
This model is designed to be used in the inference pipeline of the Tenacious Conversion Engine. When the generation agent drafts an email, this judge model scores the draft. If the judge outputs `FAIL`, the generation agent is prompted to try again (rejection sampling).

## Evaluation Results
On the 20% held-out test set from Tenacious-Bench:
- **Baseline Accuracy (Prompt-only):** ~65%
- **Trained Judge Accuracy:** ~92%
- **Delta Improvement:** +27%
- **Latency Impact:** ~85ms per task

## Limitations
- The model is strictly calibrated to the **Tenacious Style Guide** and may penalize perfectly acceptable emails from other companies if they use banned phrases like "world-class".
- As a 0.5B parameter model, it struggles with highly complex, multi-turn conversational nuances and is best used for first-touch cold outbound evaluation.
