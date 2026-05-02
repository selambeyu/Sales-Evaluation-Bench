# Synthesis Memo: LLM-as-a-Judge for Automated Evaluation
**Paper:** *A Survey on LLM-as-a-Judge* (Gu et al., 2025)

## Summary
This survey provides a comprehensive taxonomy of the "LLM-as-a-Judge" paradigm, where a frontier model (like GPT-4o or Claude 3.5) is used to score the performance of smaller models. It highlights the benefits of scalability and alignment with human judgment, but warns against "positional bias," "verbosity bias," and "self-enhancement bias" (where models prefer their own outputs).

## Key Insights for Tenacious-Bench
1. **Rubric-Based Evaluation:** The survey confirms that providing the judge with a fine-grained, multi-dimensional rubric (like our Tenacious Tone and Grounding markers) significantly increases inter-rater agreement and reduces "randomness" in scores.
2. **Preference Leakage:** A critical warning is issued regarding using the same model family for both generation and judging, which can artificially inflate scores.

## Critical Disagreement
The paper suggests that **Reference-based judging** (comparing the candidate to a "gold standard" answer) is generally superior to **Reference-free judging** (judging the candidate based on a rubric alone).

**My Disagreement:** For the **Tenacious-Bench**, reference-based judging is actually **harmful**. In B2B sales outreach, there is no single "perfect" email. If we provide a reference answer, the judge will inevitably penalize creative but valid drafts that use different (but professional) language than the reference. For our specific failure mode—Signal Over-Claiming—the judge needs to evaluate the **logical consistency** between the *hiring brief* and the *candidate email*, not compare the email to a static template. A reference-free approach anchored to a strict rubric (Grounding, Honesty, Tone) is more robust for our domain.
