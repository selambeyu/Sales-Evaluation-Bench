# Datasheet for Tenacious-Bench v0.1

## Motivation
**For what purpose was the dataset created?**
Tenacious-Bench was created to evaluate B2B conversational sales agents on their adherence to the Tenacious Style Guide, specifically targeting the "Signal Over-Claiming" failure mode identified in prior iterations.

**Who created the dataset?**
The engineering team at Tenacious Consulting.

## Composition

### Telescopic
The dataset is composed of 250 evaluation tasks for B2B conversational sales agents. Each instance consists of a prospect's Hiring Signal Brief, a Tenacious Bench Summary, a Candidate Output, and a strict Scoring Rubric.

### Periscopic
The 250 tasks are rigorously partitioned to prevent contamination and support robust evaluation and training:
- **Train Partition:** 125 tasks (50%)
- **Dev Partition:** 75 tasks (30%)
- **Held-out Partition:** 50 tasks (20%)

The tasks are distributed across the following core failure dimensions:
- **Signal Over-Claiming:** 120 tasks
- **Tone Drift / Condescension:** 80 tasks
- **Hallucinated Capacity:** 50 tasks

### Microscopic
Each instance is stored as a JSON object containing nested fields for `hiring_signal_brief` (firmographics, AI maturity, hiring velocity), `bench_summary` (engineer availability), the generated `candidate_output` string, and the `rubric` dictionary mapping 5 tone markers to their scoring criteria.

## Collection Process

### Telescopic
Data was acquired through a four-pronged synthesis approach utilizing historical traces, programmatic generation, multi-LLM synthesis, and hand-authored adversarial probes.

### Periscopic
The distribution of acquisition methods is designed to balance scale with high-fidelity edge cases:
- **Trace-derived (30% / 75 tasks):** Extracted from actual `prospect_runs.jsonl` logs from the Week 10 Conversion Engine.
- **Programmatic (30% / 75 tasks):** Generated via slot-filling templates using `ai_maturity` and `segment` parameters.
- **Multi-LLM Synthesis (25% / 62 tasks):** Generated using a rotating pool of models via OpenRouter to create specific failure edge cases, preventing preference leakage.
- **Hand-authored (15% / 38 tasks):** Human-written adversarial probes designed to break simple instruction-following LLMs.

### Microscopic
For Trace-derived tasks, raw logs were parsed and sensitive PII was scrubbed before reformatting into the Tenacious-Bench schema. For Multi-LLM Synthesis, a dev-tier model generated variations which were then strictly filtered using an LLM-as-a-judge (`scoring_evaluator.py`).

## Preprocessing/Cleaning
**Was any preprocessing/cleaning/labeling of the data done?**
All tasks generated via LLM synthesis were strictly filtered using an LLM-as-a-judge (`scoring_evaluator.py`) to ensure quality before inclusion. Contamination checks (8-gram overlap) were run to ensure absolute isolation of the held-out set.

## Uses
**Has the dataset been used for any tasks already?**
This dataset is intended to be used to train a Preference-Tuned Judge (critic model) via SimPO/ORPO to reject over-claiming drafts.

## Distribution
**Will the dataset be distributed to third parties outside of the entity?**
Yes, it is to be published on HuggingFace Hub under a CC-BY-4.0 license as a community resource for B2B sales evaluation.

## Maintenance
**Who is maintaining the dataset?**
The Tenacious Consulting engineering team.

**How will updates be communicated?**
Updates to the dataset (e.g., v0.2 to capture additional failure modes like Public-Signal Lossiness) will be versioned and published on the HuggingFace Hub repository. We will track issues via the HuggingFace discussion tab.
