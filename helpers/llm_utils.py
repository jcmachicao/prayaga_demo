from config import client, MODEL_NAME, PREFERRED_WORD_TARGET
import openai
import json
import re

def call_llm(messages, temperature=0.2, max_tokens=800):
    resp = client.responses.create(
        model=MODEL_NAME,
        input=messages,
        temperature=temperature,
        max_output_tokens=max_tokens,
    )
    
    r1 = resp.output[0].content[0].text
    return r1


def extract_json(text: str):
    match = re.search(r"{.*}", text, flags=re.DOTALL)
    if not match:
        raise ValueError("JSON not found in LLM output")
    return json.loads(match.group(0))


def build_improvement_prompt(instructions, checklist, draft, prev=None):
    checklist_text = "\n".join([f"- [{c['id']}]: {c['item']}" for c in checklist])

    system = (
        "You are an expert editor. Improve the user's text so it satisfies "
        "the instructions and checklist. Aim for ~"
        f"{PREFERRED_WORD_TARGET} words if enough info exists."
    )

    user = (
        f"Instructions:\n{instructions}\n\n"
        f"Checklist:\n{checklist_text}\n\n"
        f"User draft:\n{draft}\n\n"
    )

    if prev:
        user += f"Previous improved version:\n{prev}\n\n"

    user += (
        "Return only JSON: { \"improved\": \"...\" }"
    )

    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]


def build_evaluation_prompt(instructions, checklist, text):
    checklist_lines = "\n".join([f"{c['id']}. {c['item']}" for c in checklist])

    system = (
        "You are a strict evaluator. Return PASS/FAIL for each checklist item."
    )

    user = (
        f"Instructions:\n{instructions}\n\n"
        f"Checklist:\n{checklist_lines}\n\n"
        f"Text to evaluate:\n{text}\n\n"
        "Return JSON with keys: items[], overall_score, tone_match, tone_comment"
    )

    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
