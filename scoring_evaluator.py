import json
import os
import argparse
from typing import Dict, Any, Literal
from pydantic import BaseModel, Field

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

# Ensure OPENROUTER_API_KEY is set in the environment
api_key = os.getenv("OPENROUTER_API_KEY")
if not api_key:
    print("Warning: OPENROUTER_API_KEY environment variable not set. Evaluator will fail if run without it.")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key or "dummy_key",
)

class EvaluationResult(BaseModel):
    direct_score: int = Field(ge=1, le=5, description="Score for Direct marker (1-5)")
    direct_reasoning: str
    grounded_score: int = Field(ge=1, le=5, description="Score for Grounded marker (1-5)")
    grounded_reasoning: str
    honest_score: int = Field(ge=1, le=5, description="Score for Honest marker (1-5)")
    honest_reasoning: str
    professional_score: int = Field(ge=1, le=5, description="Score for Professional marker (1-5)")
    professional_reasoning: str
    non_condescending_score: int = Field(ge=1, le=5, description="Score for Non-condescending marker (1-5)")
    non_condescending_reasoning: str
    banned_phrase_used: bool = Field(description="True if any banned phrases were used.")
    passes_linkedin_roast: bool = Field(description="True if the email would survive the LinkedIn-Roast test without brand damage.")
    final_decision: Literal["PASS", "FAIL"] = Field(description="PASS if all scores >= 4 and no banned phrases used.")

def evaluate_task(task_data: Dict[str, Any], model: str = "openai/gpt-4o-mini") -> dict:
    """Evaluates a candidate output using an LLM-as-a-judge."""
    
    system_prompt = """You are an expert B2B Sales Evaluator acting as a strict judge for Tenacious Consulting and Outsourcing.
You will be provided with:
1. The prospect's Hiring Signal Brief (data context).
2. The Tenacious Bench Summary (availability of engineers).
3. The Candidate Output (an email draft written by an AI agent).
4. A Rubric based on the Tenacious Style Guide.

Your job is to strictly grade the Candidate Output on five Tone Markers (Direct, Grounded, Honest, Professional, Non-condescending) on a scale of 1 to 5.
Any score below 4 constitutes a failure for that marker.
You must also check for banned phrases ("world-class", "top talent", "A-players", "rockstar", "ninja", "skyrocket", "I hope this email finds you well", "just following up", "quick question", "synergize").
Finally, apply the LinkedIn-Roast test: If this email was screenshotted and posted on LinkedIn, would it damage Tenacious's brand?

Provide your response strictly adhering to the JSON schema requested."""

    user_prompt = f"""
Input Context:
{json.dumps(task_data['input'], indent=2)}

Rubric:
{json.dumps(task_data['rubric'], indent=2)}

Candidate Output to Evaluate:
\"\"\"
{task_data['candidate_output']}
\"\"\"
"""

    response = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_format=EvaluationResult,
        temperature=0.0
    )
    
    return json.loads(response.choices[0].message.content)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Tenacious-Bench scoring evaluator on a task file.")
    parser.add_argument("--task-file", type=str, required=True, help="Path to the JSON task file.")
    parser.add_argument("--model", type=str, default="anthropic/claude-3.5-sonnet", help="OpenRouter model to use as judge.")
    
    args = parser.parse_args()
    
    with open(args.task_file, "r") as f:
        task_data = json.load(f)
        
    result = evaluate_task(task_data, model=args.model)
    print(json.dumps(result, indent=2))
