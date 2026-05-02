# Methodology Rationale: Path B Preference-Tuned Critic

## Path Selection
We have selected **Path B: DPO/ORPO/SimPO a judge or critic**. 

The primary goal of this intervention is to solve the **Signal Over-Claiming** failure mode identified during the Week 10 audit of the Tenacious Conversion Engine.

## Evidence from Week 10 Traces
Our audit of historical traces and active probing (`PROBE-005`) revealed that the engine consistently hallucinates confidence when processing low-certainty public signals.
1. **Trace `trace_id_8f3a2`**: The agent asserted "I see you are scaling aggressively" based solely on a single open role for a Junior Developer, a clear case of over-claiming.
2. **Trace `trace_id_9b1c4`**: The agent pitched a full-scale AI transformation strategy to a company with an AI-Maturity Score of 1, ignoring the "Honest" marker of the Style Guide.
3. **Trace `trace_id_2c4d5`**: The agent demonstrated "Tone Drift" (Condescension), suggesting a CTO's current team was "lacking world-class potential," a high-risk brand failure.

These traces prove that the failure is not one of basic English capability (the emails were fluent), but of **calibration and style-guide alignment**.

## Theoretical Justification
Based on our review of current literature (see `synthesis_memos/path_b_memos.md`), Path B is the most robust solution for the following reasons:

### 1. Robustness to Distribution Shift
As shown in the **SimPO (Meng et al., 2024)** paper, preference tuning directly on the log-probability margins of the model's own outputs is more effective at enforcing stylistic constraints than standard SFT. By training on (chosen, rejected) pairs where the chosen response hedges and the rejected response over-claims, we bake the "Grounded" marker directly into the model's likelihood surface.

### 2. Efficiency in Low-Data Regimes
The **ORPO (Hong et al., 2024)** paper demonstrates that we can achieve high-quality alignment without a separate reference model. This allows us to train a high-performing critic on a small dataset (~50-100 high-quality preference pairs) within our compute constraints, matching the performance that would typically require thousands of SFT examples.

### 3. Scalable Evaluation
Following the **Prometheus 2 (Kim et al., 2024)** findings, we are deploying this model as a "specialized judge." Rather than a general-purpose generator, a Path B critic provides a binary or multi-dimensional "Stop/Go" signal in production, which is more reliable for automated brand-safety than re-prompting a large model.

## Conclusion
Path B provides the highest "Delta B" potential (improvement over prompting alone) because it teaches the model the exact boundary of the Tenacious Style Guide that a general-purpose model's system prompt cannot consistently enforce.
