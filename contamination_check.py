import json
import os
from collections import Counter

def get_ngrams(text, n=8):
    words = text.lower().split()
    return [" ".join(words[i:i+n]) for i in range(len(words)-n+1)]

def check_contamination(train_file, held_out_file):
    if not os.path.exists(train_file) or not os.path.exists(held_out_file):
        print("Dataset partitions not found. Run filter_and_split.py first.")
        return

    train_ngrams = set()
    with open(train_file, "r") as f:
        for line in f:
            if not line.strip(): continue
            task = json.loads(line)
            # We check overlap on input fields per the spec
            text = json.dumps(task["input"])
            train_ngrams.update(get_ngrams(text))

    results = {
        "metrics": {
            "total_held_out_tasks": 0,
            "tasks_with_overlap": 0,
            "overlap_percentage": 0.0,
            "n_gram_size": 8
        },
        "contaminated_task_ids": [],
        "status": "PASS"
    }

    with open(held_out_file, "r") as f:
        for line in f:
            if not line.strip(): continue
            task = json.loads(line)
            results["metrics"]["total_held_out_tasks"] += 1
            text = json.dumps(task["input"])
            held_out_ngrams = set(get_ngrams(text))
            
            overlap = train_ngrams.intersection(held_out_ngrams)
            if overlap:
                results["metrics"]["tasks_with_overlap"] += 1
                results["contaminated_task_ids"].append(task['task_id'])

    if results["metrics"]["total_held_out_tasks"] > 0:
        results["metrics"]["overlap_percentage"] = (results["metrics"]["tasks_with_overlap"] / results["metrics"]["total_held_out_tasks"]) * 100

    if results["metrics"]["tasks_with_overlap"] > 0:
        results["status"] = "FAIL"
        
    with open("contamination_check.json", "w") as out:
        json.dump(results, out, indent=2)
        
    print(f"Contamination check completed. Status: {results['status']}. See contamination_check.json for details.")

if __name__ == "__main__":
    train_path = "tenacious_bench_v0.1/train/data.jsonl"
    held_out_path = "tenacious_bench_v0.1/held_out/data.jsonl"
    check_contamination(train_path, held_out_path)
