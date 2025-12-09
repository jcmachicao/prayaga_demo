from .llm_utils import call_llm, extract_json, build_improvement_prompt, build_evaluation_prompt
from config import MAX_ITERATIONS

def improve_and_evaluate(instructions, checklist, draft, prev=None):

    # 1. Improve
    imp_prompt = build_improvement_prompt(instructions, checklist, draft, prev)
    raw_improved = call_llm(imp_prompt, temperature=0.1)

    try:
        improved = extract_json(raw_improved)["improved"].strip()
    except:
        improved = raw_improved.strip()

    # 2. Evaluate
    eval_prompt = build_evaluation_prompt(instructions, checklist, improved)
    raw_eval = call_llm(eval_prompt, temperature=0.0)

    try:
        evaluation = extract_json(raw_eval)
    except:
        evaluation = {"error": "Evaluation JSON parse failed"}

    return improved, evaluation

def checklist_passed(eval_json: dict) -> bool:
    items = eval_json.get("items", [])
    for item in items:
        result = item.get("result") or item.get("status") or item.get("pass") or item.get("outcome")
        if not result or str(result).upper() != "PASS":
            return False
    return True