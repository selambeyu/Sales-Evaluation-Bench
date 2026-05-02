import json
import os
import itertools
import random

output_file = "data/programmatic_tasks.jsonl"

def generate_programmatic_tasks():
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Define parameter spaces
    companies = ["DataFlow Inc", "NovaTech", "Acme AI", "Yellow.ai", "Pulse Dynamics"]
    segments = ["recently-funded Series A/B startups", "mid-market platforms restructuring cost", "engineering-leadership transitions", "specialized capability gaps"]
    signals = [
        {"type": "funding_event", "value": "Series B $15M"},
        {"type": "job_post_velocity", "value": "3 open engineering roles"},
        {"type": "layoffs", "value": "12% reduction in Q1"},
        {"type": "leadership_change", "value": "New CTO joined 30 days ago"}
    ]
    confidences = ["High", "Medium", "Low"]
    ai_maturities = [0, 1, 2, 3]
    
    # Combinatorial expansion
    combinations = list(itertools.product(companies, segments, signals, confidences, ai_maturities))
    random.seed(42)
    random.shuffle(combinations) # Shuffle so we can pick a subset
    
    # We want ~75 tasks for 30% of 250
    target_count = 75
    selected_combinations = combinations[:target_count]
    
    tasks = []
    for i, (comp, seg, sig, conf, ai_mat) in enumerate(selected_combinations):
        
        # Determine expected behavior (e.g., if AI maturity is 0 and segment is specialized gap -> misclassification risk)
        expected_failure = "None"
        if conf == "Low":
            expected_failure = "Signal Over-Claiming"
        elif ai_mat < 2 and seg == "specialized capability gaps":
            expected_failure = "Wrong Segment Pitch"
            
        # We leave candidate_output blank or put a dummy value. 
        # In a real programmatic pipeline, you'd feed this input to your Week 10 agent to generate the email, 
        # or use an LLM to generate the email based on the prompt template.
        candidate_output = f"Hi {comp} team, we noticed your {sig['value']}. We are a world-class team..." if conf == "Low" else f"Hi {comp}, saw the {sig['type']}."
        
        task = {
            "task_id": f"prog_{i}",
            "source_mode": "programmatic",
            "input": {
                "hiring_signal_brief": {
                    "company_name": comp,
                    "icp_segment": seg,
                    "signals": [
                        {
                            "signal_type": sig["type"],
                            "value": sig["value"],
                            "confidence": conf
                        }
                    ],
                    "ai_maturity_score": ai_mat,
                    "ai_maturity_confidence": "Medium"
                },
                "bench_summary": {"Python": 2, "Go": 1, "Data": 1, "ML": 0},
                "prior_thread": None
            },
            "candidate_output": candidate_output,
            "expected_failure_mode": expected_failure,
            "rubric": {
                "direct": "Subject states intent. Body <= 120 words. One ask.",
                "grounded": "Names specific signal from brief. Confidence-aware phrasing matches signal confidence.",
                "honest": "Names what brief does not show. Refuses to commit unsupported bench capacity.",
                "professional": "No banned phrases. No 'bench' externally.",
                "non_condescending": "Frames gaps as research findings."
            }
        }
        tasks.append(task)
        
    with open(output_file, "w") as out:
        for t in tasks:
            out.write(json.dumps(t) + "\n")
            
    print(f"Generated {len(tasks)} programmatic tasks to {output_file}")

if __name__ == "__main__":
    generate_programmatic_tasks()
