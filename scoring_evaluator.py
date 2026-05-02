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

# Ensure API keys and URLs are set in the environment
api_key = os.getenv("OPENROUTER_API_KEY")
local_llm_url = os.getenv("LOCAL_LLM_URL")
local_llm_model = os.getenv("LOCAL_LLM_MODEL")

def get_client(use_local=False):
    if use_local and local_llm_url:
        return OpenAI(
            base_url=local_llm_url,
            api_key="ollama", # Ollama doesn't need a real key
        )
    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key or "dummy_key",
    )

client = get_client(use_local=bool(os.getenv("USE_LOCAL_LLM") == "true"))

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
    
    use_local = os.getenv("USE_LOCAL_LLM") == "true"
    local_llm_model = os.getenv("LOCAL_LLM_MODEL")
    
    if use_local and local_llm_model:
        model = local_llm_model
    
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

Provide your response strictly in JSON format matching this structure:
{
  "direct_score": int,
  "direct_reasoning": string,
  "grounded_score": int,
  "grounded_reasoning": string,
  "honest_score": int,
  "honest_reasoning": string,
  "professional_score": int,
  "professional_reasoning": string,
  "non_condescending_score": int,
  "non_condescending_reasoning": string,
  "banned_phrase_used": boolean,
  "passes_linkedin_roast": boolean,
  "final_decision": "PASS" | "FAIL"
}"""

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

    if use_local:
        # Fallback for local models that don't support .parse
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.0
        )
        content = response.choices[0].message.content
        # Basic cleanup in case model includes markdown markers
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
            
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            # Secondary fallback: Regex extraction for common fields if JSON is malformed
            print(f"Error decoding JSON from local model: {e}. Attempting regex fallback...")
            try:
                import re
                result = {}
                # Extract scores
                for field in ["direct_score", "grounded_score", "honest_score", "professional_score", "non_condescending_score"]:
                    match = re.search(fr'"{field}"\s*:\s*(\d)', content)
                    if match: result[field] = int(match.group(1))
                
                # Extract reasons (greedy match until next field or end)
                for field in ["direct_reasoning", "grounded_reasoning", "honest_reasoning", "professional_reasoning", "non_condescending_reasoning"]:
                    match = re.search(fr'"{field}"\s*:\s*"(.*?)"(?=,|\s*}})', content, re.DOTALL)
                    if match: result[field] = match.group(1).strip()
                
                # Extract booleans and Literal
                match = re.search(r'"banned_phrase_used"\s*:\s*(true|false)', content)
                if match: result["banned_phrase_used"] = match.group(1) == "true"
                match = re.search(r'"passes_linkedin_roast"\s*:\s*(true|false)', content)
                if match: result["passes_linkedin_roast"] = match.group(1) == "true"
                match = re.search(r'"final_decision"\s*:\s*"(PASS|FAIL)"', content)
                if match: result["final_decision"] = match.group(1)
                
                # Validate we have enough fields
                if "final_decision" in result:
                    return result
            except Exception as re_err:
                print(f"Regex fallback failed: {re_err}")
                
            print(f"Raw content: {content}")
            raise
    else:
        # Use structured output for supported models (OpenRouter/OpenAI)
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
