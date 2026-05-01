import json
import os
import random
import sys

# Add parent directory to path to import scoring_evaluator
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from scoring_evaluator import evaluate_task
except ImportError:
    print("Warning: Could not import scoring_evaluator.py")
    evaluate_task = None

input_files = [
    "data/trace_derived_tasks.jsonl",
    "data/programmatic_tasks.jsonl",
    "data/synthesized_tasks.jsonl",
    "data/hand_authored_tasks.jsonl"
]
output_dir = "tenacious_bench_v0.1"

def split_tasks():
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(f"{output_dir}/train", exist_ok=True)
    os.makedirs(f"{output_dir}/dev", exist_ok=True)
    os.makedirs(f"{output_dir}/held_out", exist_ok=True)
    
    all_tasks = []
    
    for file in input_files:
        if os.path.exists(file):
            with open(file, "r") as f:
                for line in f:
                    if line.strip():
                        all_tasks.append(json.loads(line))
                        
    print(f"Total raw tasks loaded: {len(all_tasks)}")
    
    valid_tasks = []
    if evaluate_task:
        print("Filtering tasks using LLM judge...")
        for task in all_tasks:
            try:
                # evaluate_task expects a dict and optionally a model argument
                result = evaluate_task(task)
                if result.get("final_decision") == "PASS":
                    valid_tasks.append(task)
            except Exception as e:
                print(f"Error evaluating task {task.get('task_id')}: {e}")
                # Fallback: if evaluation fails, we might still include it or exclude it. 
                # Strict filtering means exclude.
    else:
        print("scoring_evaluator not found. Assuming all tasks are valid.")
        valid_tasks = all_tasks
        
    print(f"Tasks passed filter: {len(valid_tasks)} / {len(all_tasks)}")
    
    # Shuffle and split: 50% train, 30% dev, 20% held_out
    random.seed(42)
    random.shuffle(valid_tasks)
    
    n = len(valid_tasks)
    train_idx = int(n * 0.5)
    dev_idx = train_idx + int(n * 0.3)
    
    train_tasks = valid_tasks[:train_idx]
    dev_tasks = valid_tasks[train_idx:dev_idx]
    held_out_tasks = valid_tasks[dev_idx:]
    
    def save_split(split_name, tasks):
        path = f"{output_dir}/{split_name}/data.jsonl"
        with open(path, "w") as out:
            for t in tasks:
                out.write(json.dumps(t) + "\n")
        print(f"Saved {len(tasks)} tasks to {path}")
        
    save_split("train", train_tasks)
    save_split("dev", dev_tasks)
    save_split("held_out", held_out_tasks)

if __name__ == "__main__":
    split_tasks()
