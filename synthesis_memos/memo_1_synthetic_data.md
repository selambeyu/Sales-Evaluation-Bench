# Synthesis Memo 1: Disagreeing with "Best Practices and Lessons Learned on Synthetic Data"

**Paper:** *Best Practices and Lessons Learned on Synthetic Data for Language Models* (Liu et al., COLM 2024)

## Design Choice in the Paper
Liu et al. suggest that synthetic data generation, particularly through programmatic variation and self-instruction techniques, can achieve sufficient coverage and quality to substitute for human-labeled data in many alignment and evaluation tasks. They emphasize that scaling synthetic permutations over fixed templates is an effective strategy for robustness.

## Disagreement Based on Week 10 Evidence
While programmatic generation is excellent for covering surface-level combinations (e.g., sweeping across different ICP segments and company sizes), our Week 10 trace evidence demonstrates that it is fundamentally insufficient for capturing the most expensive failure modes in B2B conversational sales.

Specifically, the "Signal Over-Claiming" and "Tone Drift" failures identified in `failure_taxonomy.md` rarely manifest in clean, programmatic ways. In `trace_log.jsonl`, the Conversion Engine didn't fail because it couldn't handle a Segment 4 company. It failed because it encountered a probabilistically weak signal (only 2 open roles) and its instruction-following bias caused it to hallucinate an overly confident assertion ("you are scaling aggressively") to sound helpful. 

Programmatic templates struggle to artificially inject this kind of nuanced "helpful-but-wrong" hallucination. Our attempt to generate these via pure template slot-filling produced wooden, easily detectable errors rather than the subtle, insidious tone drift seen in actual agent traces. Therefore, we disagree that synthetic permutation can fully substitute for trace-derived data when evaluating nuanced, tone-based brand risks. Trace-derived tasks (which make up ~30% of Tenacious-Bench) remain the only high-fidelity measure for these specific failures.
