# Audit Memo: The Gap in Public Benchmarks for Tenacious B2B Sales

## The Core Gap
Existing conversational agent benchmarks, such as the τ²-Bench retail domain, are exceptional at testing dual-control coordination, instruction following, and task completion within well-bounded, rule-driven environments. However, they fundamentally fail to evaluate the most critical brand-risk axis for Tenacious Consulting and Outsourcing: **Signal-Confidence Calibration** and **Over-Claiming**.

In a retail benchmark, the ground truth is binary (e.g., the user either wants to return an item or does not). In Tenacious's B2B outbound workflow, the ground truth is probabilistic. An agent must infer a prospect's intent from weak, public signals (e.g., job posting velocity, recent layoffs, or AI-adjacent keywords). 

## The Failure Taxonomy
To understand the scope of this gap, we audited our Week 10 probes and historical traces (`probe_library.md` and `trace_log.jsonl`) and developed a comprehensive `failure_taxonomy.md`. We identified 10 core failure modes. The two most distinct and critical gaps that public benchmarks fail to measure are:
1. **Signal Over-Claiming:** The agent asserts strong claims from weak probabilistic signals.
2. **Tone Drift (Condescension):** The agent frames a prospect's lack of capability as a failure rather than an opportunity, sounding presumptuous.

## Evidence from Week 10
During Week 10 probing (`PROBE-005`), we identified that the Conversion Engine consistently suffers from these two failures. 
For **Signal Over-Claiming**, as seen in `trace_id_8f3a2` and `trace_id_9b1c4`, the agent repeatedly sent emails starting with, "I see you are scaling aggressively" when the underlying data only showed two open roles. This occurs because LLMs are fine-tuned to be helpful and confident, fabricating certainty from ambiguous data.
For **Tone Drift**, as seen in `trace_id_2c4d5`, the agent used phrases like "you clearly lack the top talent needed to succeed," which would permanently burn a CTO relationship.

The business impact of this failure mode is severe. Across our 1,001 Crunchbase sample, approximately 35% of targeted prospects had medium or low-confidence signals. The agent hallucinated certainty and over-claimed in roughly 20% of these cases. According to Tenacious's unit economics (average ACV $480K, 42% discovery-to-proposal conversion), losing a prospect due to brand-damaging, wrong-signal outreach costs the firm an expected **$64,512 per wrong email**. At current volume targets, this translates to **~$107K in weekly ACV at risk**. 

## Why τ²-Bench Misses This
τ²-Bench does not capture this because:
1. **No Uncertainty Modeling:** It provides the agent with absolute facts rather than probabilistic public-signal briefs.
2. **No Tone-Preservation Penalties:** It does not penalize an agent for sounding presumptuous, condescending, or using offshore vendor clichés ("world-class", "top talent").
3. **No Downstream Brand Damage:** In a generic benchmark, a wrong answer simply lowers the pass@1 score. In B2B sales, a condescending email to a CTO burns that account for years.

## The Solution: Tenacious-Bench
To solve this, we must build **Tenacious-Bench v0.1**. This dataset will specifically test the agent's ability to:
1. **Hedge on Weak Signals:** Ask questions instead of making assertions when signal confidence is low.
2. **Adhere to the Style Guide:** Maintain a direct, grounded, honest, professional, and non-condescending tone.
3. **Avoid Banned Phrasing:** Never use phrases that trigger spam filters or offshore-vendor prejudice.

By grading the agent on these specific dimensions using a calibrated LLM-as-a-judge, we can train a model (via Preference Tuning) to act as a strict critic, fundamentally resolving the ~$107K/week brand risk.
