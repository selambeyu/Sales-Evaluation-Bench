# Synthesis Memo: Data Contamination in LLM Evaluation
**Paper:** *Recent Advances in Large Language Model Benchmarks against Data Contamination: From Static to Dynamic Evaluation* (Chen et al., EMNLP 2025)

## Summary
The paper identifies data contamination—where evaluation data is leaked into the training set of large models—as a primary threat to the validity of LLM benchmarks. It categorizes contamination into "input-level" (memorization) and "output-level" (answer leakage) and proposes a move from static benchmarks to dynamic, procedurally generated evaluation sets.

## Key Insights for Tenacious-Bench
1. **Multi-Faceted Detection:** The authors argue that simple n-gram overlap checks are no longer sufficient. Modern contamination detection requires semantic (embedding-based) checks and "cross-model" verification to identify if a model is relying on memorized patterns.
2. **Dynamic Evolution:** The paper advocates for "live" benchmarks where tasks are refreshed or perturbed regularly to prevent static leakage in the training corpora of frontier models.

## Critical Disagreement
The authors place a heavy emphasis on **Dynamic Evaluation** (changing the questions over time) as the "gold standard" for reliability. 

**My Disagreement:** While dynamic evaluation is ideal for general-purpose benchmarks (like MMLU), it is counter-productive for specialized B2B sales benchmarks like **Tenacious-Bench**. In a production enterprise environment, we need **comparative stability**. If our bench shifts every week, we cannot definitively say that a new iteration of our Conversion Engine is better than the last; we wouldn't know if the score moved because the model improved or because the "dynamic" tasks got easier. For Tenacious, a "Locked and Sealed" held-out partition—protected by strict n-gram and embedding filters—is more valuable for engineering progress than a constantly shifting target.
