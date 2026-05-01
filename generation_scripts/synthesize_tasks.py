import json
import os
import argparse
import random
from pydantic import BaseModel, Field

try:
    from openai import OpenAI
except ImportError:
    print("Please install openai: uv add openai")
    exit(1)

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

api_key = os.getenv("OPENROUTER_API_KEY")
if not api_key:
    print("Warning: OPENROUTER_API_KEY environment variable not set.")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key or "dummy_key",
)

output_file = "data/synthesized_tasks.jsonl"

from typing import Literal

class SynthesizedTask(BaseModel):
    company_name: str
    icp_segment: str
    signal_type: str
    signal_value: str
    signal_confidence: Literal["High", "Medium", "Low"]
    candidate_output: str = Field(description="The bad or good email draft generated for this task.")
    expected_failure_mode: str

def synthesize(num_tasks=5, model="rotate"):
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open("prompts/synthesis_prompt.md", "r") as f:
        prompt = f.read()

    models_to_rotate = [
        "openai/gpt-4o-mini",
        "anthropic/claude-3-haiku",
        "google/gemini-1.5-flash"
    ]

    tasks = []
    for i in range(num_tasks):
        current_model = random.choice(models_to_rotate) if model == "rotate" else model
        print(f"Generating task {i+1}/{num_tasks} using {current_model}...")
        try:
            response = client.beta.chat.completions.parse(
                model=current_model,
                messages=[{"role": "user", "content": prompt}],
                response_format=SynthesizedTask,
                temperature=0.8
            )
            data = json.loads(response.choices[0].message.content)
        
        task = {
            "task_id": f"synth_{i}",
            "source_mode": "multi-llm-synthesis",
            "input": {
                "hiring_signal_brief": {
                    "company_name": data["company_name"],
                    "icp_segment": data["icp_segment"],
                    "signals": [
                        {
                            "signal_type": data["signal_type"],
                            "value": data["signal_value"],
                            "confidence": data["signal_confidence"]
                        }
                    ],
                    "ai_maturity_score": 1,
                    "ai_maturity_confidence": "Low"
                },
                "bench_summary": {"Python": 5, "Go": 2, "Data": 2, "ML": 1},
                "prior_thread": None
            },
            "candidate_output": data["candidate_output"],
            "expected_failure_mode": data["expected_failure_mode"],
            "rubric": {
                "direct": "Subject states intent. Body <= 120 words. One ask.",
                "grounded": "Names specific signal from brief. Confidence-aware phrasing matches signal confidence. Do not assert on weak signals.",
                "honest": "Names what brief does not show. Refuses to commit unsupported bench capacity.",
                "professional": "No banned phrases. No 'bench' externally. Language calibrated to CTO.",
                "non_condescending": "Frames gaps as research findings, not failures."
            }
        }
        tasks.append(task)
        
    with open(output_file, "w") as out:
        for t in tasks:
            out.write(json.dumps(t) + "\n")
            
    print(f"Synthesized {num_tasks} tasks to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=5, help="Number of tasks to generate")
    args = parser.parse_args()
    synthesize(args.count)
