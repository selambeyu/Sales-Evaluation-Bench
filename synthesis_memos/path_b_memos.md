# Synthesis Memo: Preference Tuning for Judge/Critic Models (Path B)

This memo synthesizes the theoretical foundations for the **Path B** approach: training a preference-tuned judge or critic model using reference-free alignment techniques (ORPO/SimPO) and evaluating it with a calibrated judge (Prometheus 2).

## 1. DPO (Direct Preference Optimization)
**Rafailov et al. (2023)**
DPO revolutionized LLM alignment by eliminating the need for a separate Reward Model (RM) and the complex, unstable Reinforcement Learning from Human Feedback (RLHF) loop. Instead, it directly optimizes the policy using a simple binary cross-entropy loss on preference pairs.
- **Application for Tenacious-Bench:** Provides the baseline for understanding how to align a model with the Tenacious Style Guide by comparing "chosen" (Style Guide compliant) vs. "rejected" (over-claiming) outputs.

## 2. ORPO (Odds Ratio Preference Optimization)
**Hong et al. (2024)**
ORPO improves upon DPO by combining the Supervised Fine-Tuning (SFT) and alignment phases into a single objective. It uses an odds ratio loss to penalize the model for assigning high probability to rejected responses relative to chosen ones.
- **Why it fits Path B:** It is memory-efficient and doesn't require a reference model, making it ideal for the limited compute budget (free Colab T4) of the Tenacious Sales Bench.

## 3. SimPO (Simple Preference Optimization)
**Meng et al. (2024)**
SimPO is a simpler, reference-free alternative to DPO that uses a length-normalized reward based on log-probabilities. It directly optimizes the margin between chosen and rejected responses without the KL-divergence penalty.
- **Why it fits Path B:** It often outperforms DPO on reasoning and instruction-following benchmarks while being even lighter to train. For a "Critic" model, the length-normalization helps avoid the bias toward longer (but potentially more hallucinated) emails.

## 4. Prometheus 2: An Open Source Language Model for Evaluation
**Kim et al. (2024)**
Prometheus 2 is a specialized LLM trained to simulate human evaluation using custom rubrics. It proves that a smaller, specialized model can match or exceed GPT-4 performance in "LLM-as-a-Judge" tasks if provided with precise scoring instructions.
- **Application for Tenacious-Bench:** Validates our use of a 1.5B/2B/4B backbone as a production judge. By training on Tenacious-specific failure modes, we are essentially building a specialized "Tenacious-Prometheus" for sales outreach audit.

## Synthesis & Implementation
For the Tenacious Sales Evaluation Bench, we will prioritize **ORPO** or **SimPO** for training our Path B judge. The target failure mode—**Signal Over-Claiming**—requires the model to learn a subtle distinction between confidence and accuracy. By training on preference pairs where the "chosen" response hedges on weak signals and the "rejected" response over-claims, we create a high-precision rollback layer that can be deployed as an automated quality gate in the Tenacious Conversion Engine.
