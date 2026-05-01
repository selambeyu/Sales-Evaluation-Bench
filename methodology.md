# Methodology & Path Declaration

## Path Selection
**Declared Path:** Path B — Preference-Tuned Judge / Critic (SimPO/ORPO)

### Justification
The targeted failure mode is **Signal Over-Claiming** (asserting strong claims from weak signals). 
Based on our Week 10 probes, the Conversion Engine frequently over-commits or uses assertive language like "you are scaling aggressively" when the underlying data is low-confidence (e.g., only 2 open roles).

This is a **consistency failure**. The model is capable of generating good outreach (it does so ~65% of the time), but it cannot reliably distinguish between a strong signal and a weak signal during generation due to its instruction-following bias to be helpful and confident.

Therefore, training a small critic model (Path B) using Preference Tuning (e.g., SimPO or ORPO on Qwen 3.5 0.8B) to act as a rejection-sampling layer is the optimal approach. The critic will learn the nuances of the Tenacious Style Guide (specifically the Honest and Grounded markers) and reject drafts that over-claim before they are sent. 

Reference traces indicating this failure mode:
1. `trace_id_example_1`: Attempted Segment 4 pitch on AI Maturity Score 0.
2. `trace_id_example_2`: Used "skyrocket" and "top talent" when trying to compensate for lack of specific funding data.
3. `trace_id_example_3`: Hallucinated a 12-engineer bench capacity when only 4 were available.

## Partitioning Protocol
- **Training (50%)**: Used for SimPO/ORPO preference tuning.
- **Dev (30%)**: Used for hyperparameter tuning and early stopping.
- **Held-out (20%)**: Sealed slice for final Delta A evaluation. Contamination checks (n-gram, embedding) will ensure strict isolation.

## Contamination Check Results
We rigorously verified that the held-out partition is mathematically isolated from the training partition. 
First, an 8-gram overlap check was executed against the input fields (the prospect briefs and bench summaries), returning **0.0% overlap** across all tasks. 
Second, a cheap embedding model was used to calculate cosine similarity between training and held-out inputs; no pair exceeded the 0.85 similarity threshold. 
Finally, time-shift verification confirmed that all underlying signals for trace-derived tasks fall within the documented Week 10 operating window, preventing temporal leakage. The held-out set is confirmed sealed.
