import json
import os
import sys

# Add parent directory to path to import scoring_evaluator
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scoring_evaluator import evaluate_task

try:
    from openai import OpenAI
except ImportError:
    print("Please install openai: pip install openai")
    exit(1)

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

api_key = os.getenv("OPENROUTER_API_KEY")
local_llm_url = os.getenv("LOCAL_LLM_URL")
local_llm_model = os.getenv("LOCAL_LLM_MODEL")
use_local = os.getenv("USE_LOCAL_LLM") == "true"

def get_client():
    if use_local and local_llm_url:
        return OpenAI(
            base_url=local_llm_url,
            api_key="ollama",
        )
    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key or "dummy_key",
    )

client = get_client()

input_file = "../tenacious_bench_v0.1/train/data.jsonl"
output_file = "../tenacious_bench_v0.1/train/preference_data.jsonl"

# Use local model if specified, otherwise default to OpenRouter models
REWRITE_MODEL = local_llm_model if use_local else "google/gemini-2.5-flash-8b"
EVAL_MODEL = local_llm_model if use_local else "openai/gpt-4o-mini"
MAX_RETRIES = 3

def rewrite_task(task: dict) -> str:
    """Uses a dev-tier model to rewrite a failed candidate output into a chosen output."""
    
    system_prompt = """You are an expert B2B Sales writer for Tenacious Consulting. 
Your task is to fix a rejected email draft.
The draft failed because it violated the Tenacious Style Guide. 

Style Guide:
- Direct: Subject states intent. Body <= 120 words. One ask.
- Grounded: Names specific signal from brief. Confidence-aware phrasing matches signal confidence. Do not assert on weak signals (e.g. 1 open role). Instead of claiming they are scaling aggressively, ask if they are exploring team expansion.
- Honest: Names what brief does not show. Refuses to commit unsupported bench capacity.
- Professional: No banned phrases ("world-class", "top talent", "A-players", "rockstar", "ninja", "skyrocket", "I hope this email finds you well", "just following up", "quick question", "synergize", "bench").
- Non-condescending: Frames gaps as research findings, not failures.

Fix the draft to pass the Style Guide. Return ONLY the new email text, no conversational filler."""

    user_prompt = f"""
Input Context (Hiring Signal & Bench):
{json.dumps(task['input'], indent=2)}

Original Failed Draft:
\"\"\"
{task['candidate_output']}
\"\"\"

Failure Mode to Fix: {task['expected_failure_mode']}

Provide the revised email draft:
"""

    response = client.chat.completions.create(
        model=REWRITE_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.3
    )
    
    return response.choices[0].message.content.strip()

def prepare_data():
    if not os.path.exists(input_file):
        print(f"File not found: {input_file}")
        return

    pairs = []
    
    with open(input_file, "r") as f:
        tasks = [json.loads(line) for line in f if line.strip()]

    # We only process tasks that are expected to fail (so we have a 'rejected' output)
    failed_tasks = [t for t in tasks if t.get("expected_failure_mode", "None") != "None"]
    print(f"Found {len(failed_tasks)} failed tasks to rewrite into preference pairs.")

    for i, task in enumerate(failed_tasks):
        print(f"Processing task {i+1}/{len(failed_tasks)}: {task['task_id']}")
        
        prompt_text = f"Context: {json.dumps(task['input']['hiring_signal_brief'])}\nWrite an outreach email."
        rejected_text = task["candidate_output"]
        
        chosen_text = None
        for attempt in range(MAX_RETRIES):
            # 1. Generate rewrite
            rewrite = rewrite_task(task)
            
            # 2. Evaluate
            test_task = task.copy()
            test_task["candidate_output"] = rewrite
            try:
                eval_result = evaluate_task(test_task, model=EVAL_MODEL)
                
                if eval_result.get("final_decision") == "PASS":
                    chosen_text = rewrite
                    print(f"  -> Success on attempt {attempt+1}")
                    break
                else:
                    print(f"  -> Attempt {attempt+1} failed evaluation.")
            except Exception as e:
                print(f"  -> Attempt {attempt+1} evaluator error: {e}")
        
        if chosen_text:
            pair = {
                "task_id": task["task_id"],
                "prompt": prompt_text,
                "chosen": chosen_text,
                "rejected": rejected_text
            }
            pairs.append(pair)
        else:
            print(f"  -> Failed to generate a PASSing rewrite for task {task['task_id']} after {MAX_RETRIES} attempts.")
            
        # Optional: early break for testing
        # if len(pairs) >= 5: break
            
    # Save the pairs
    with open(output_file, "w") as out:
        for p in pairs:
            out.write(json.dumps(p) + "\n")
            
    print(f"Successfully prepared {len(pairs)} preference pairs and saved to {output_file}")

if __name__ == "__main__":
    prepare_data()
