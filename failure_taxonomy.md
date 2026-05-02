# Tenacious B2B Sales Failure Taxonomy

Based on our audit of Week 10 probes and historical traces (`probe_library.md` and `trace_log.jsonl`), we have identified 10 core failure modes where the LLM agent deviates from the Tenacious Style Guide or makes critical business errors.

## 1. Signal Over-Claiming (Target Failure Mode)
**Description:** The agent makes strong assertions ("you are scaling aggressively") based on low-confidence or weak public signals (e.g., only 1-2 open roles).
**Impact:** Severe brand damage; sounds presumptuous to CTOs.

## 2. Hallucinated Capacity
**Description:** The agent commits to bench availability or specific technical skills (e.g., "We have 5 Rust engineers ready") that contradict the provided `bench_summary`.
**Impact:** Broken promises, loss of trust during discovery calls.

## 3. Tone Drift (Offshore Vendor Clichés)
**Description:** The agent uses banned, spam-triggering phrases common to generic offshore vendors ("world-class", "top talent", "rockstar", "skyrocket").
**Impact:** Immediate deletion by prospects; triggers spam filters.

## 4. Generic Messaging
**Description:** The email fails to mention any specific firmographic data or signals from the `hiring_signal_brief`, resulting in a generic pitch.
**Impact:** Low conversion rate; fails the "Direct & Grounded" style markers.

## 5. Condescension
**Description:** The agent frames the prospect's capability gaps as failures or mistakes rather than research findings.
**Impact:** Offends the prospect; fails the "Non-condescending" style marker.

## 6. Weak / Multiple CTAs
**Description:** The agent includes more than one "ask" in the email, or the Call to Action is vague (e.g., "Let me know your thoughts").
**Impact:** Increases cognitive load for the prospect; violates the "One Ask" rule.

## 7. Wrong Segment Pitch
**Description:** The agent pitches a value proposition intended for one segment (e.g., cost-cutting for mid-market restructuring) to a completely different segment (e.g., recently funded Series A).
**Impact:** Irrelevant messaging; lowers reply rates.

## 8. Verbosity (Word Count Violation)
**Description:** The cold outbound email exceeds the strict 120-word limit specified in the formatting constraints.
**Impact:** Visual fatigue; prospects will not read long cold emails.

## 9. Subject Line Fatigue
**Description:** The subject line is generic, clickbait, or exceeds the 60-character limit.
**Impact:** Low open rates.

## 10. Guilt Follow-ups
**Description:** In thread continuations, the agent uses phrases like "just following up" or "I haven't heard back from you."
**Impact:** Appears needy and unprofessional; explicitly banned in the Style Guide.
