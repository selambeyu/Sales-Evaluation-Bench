import json
import os

input_file = "../Conversion-Engine/logs/prospect_runs.jsonl"
output_file = "data/trace_derived_tasks.jsonl"

def extract_traces():
    if not os.path.exists(input_file):
        print(f"File {input_file} not found. Skipping trace extraction.")
        return

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    extracted_tasks = []
    with open(input_file, "r") as f:
        for i, line in enumerate(f):
            if not line.strip(): continue
            data = json.loads(line)
            
            # Restructure into Tenacious-Bench Schema format
            task = {
                "task_id": f"trace_{data.get('trace_id', i)}",
                "source_mode": "trace-derived",
                "input": {
                    "hiring_signal_brief": {
                        "company_name": data.get("company", "Unknown"),
                        "icp_segment": data.get("segment", "Unknown"),
                        "signals": [
                            {
                                "signal_type": "funding_event" if "funded" in data.get("segment", "") else "job_post_velocity",
                                "value": "Unknown",
                                "confidence": "Low"  # Defaulting to low to test over-claiming
                            }
                        ],
                        "ai_maturity_score": data.get("ai_maturity", 0),
                        "ai_maturity_confidence": "Low"
                    },
                    "bench_summary": {
                        "Python": 2, "Go": 1, "Data": 1, "ML": 0
                    },
                    "prior_thread": None
                },
                "candidate_output": data.get("email_subject", "") + "\n\n(Assume body text from trace)",
                "expected_failure_mode": "Signal Over-Claiming",
                "rubric": {
                    "direct": "Subject states intent. Body <= 120 words. One ask.",
                    "grounded": "Names specific signal from brief. Confidence-aware phrasing matches signal confidence. Do not assert on weak signals.",
                    "honest": "Names what brief does not show. Refuses to commit unsupported bench capacity.",
                    "professional": "No banned phrases. No 'bench' externally. Language calibrated to CTO.",
                    "non_condescending": "Frames gaps as research findings, not failures."
                }
            }
            extracted_tasks.append(task)
            
    with open(output_file, "w") as out:
        for t in extracted_tasks:
            out.write(json.dumps(t) + "\n")
            
    print(f"Extracted {len(extracted_tasks)} tasks to {output_file}")

if __name__ == "__main__":
    extract_traces()
