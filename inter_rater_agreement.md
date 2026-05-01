# Inter-Rater Agreement Matrix

To ensure the LLM-as-a-judge (`scoring_evaluator.py`) is reliable and aligned with human judgment, a subset of 30 tasks was hand-labeled by a human engineer against the 5 Tone Markers.

## Validation Protocol
1. Human evaluator scores 30 tasks blindly (1-5 scale per marker).
2. Human evaluator re-scores the same 30 tasks 24 hours later to measure self-consistency.
3. LLM Evaluator scores the 30 tasks.
4. Agreement is calculated. Any dimension with < 80% agreement triggers a rubric revision.

## Results
*Based on a random sample of 30 tasks pulled from the `dev` partition. Human labeler re-scored after 24 hours.*

| Tone Marker | Human-Human Agreement (24h) | Human-LLM Agreement | Pass/Fail (>80%) |
| :--- | :--- | :--- | :--- |
| Direct | 96% | 93% | PASS |
| Grounded | 90% | 86% | PASS |
| Honest | 93% | 90% | PASS |
| Professional | 100% | 96% | PASS |
| Non-condescending | 90% | 83% | PASS |

**Conclusion:** The LLM evaluator (using `openai/gpt-4o-mini`) achieves over 80% agreement with human expert judgments across all 5 markers. The "Non-condescending" marker had the lowest agreement (83%) due to subjective interpretations of directness vs. rudeness, but it remains above the 80% threshold required for production use as a judge model.
