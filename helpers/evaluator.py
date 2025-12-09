import json
from typing import Dict, Any


def evaluate_text(client, model_name: str, text: str, checklist: dict) -> Dict[str, Any]:
    """
    Sends the user's text + checklist to the LLM and requests a strict JSON evaluation.
    """

    system_prompt = f"""
You are an evaluator. Your job is to rigorously check whether the user's project text 
complies with each checklist item.

Return your response STRICTLY in valid JSON, with this exact structure:

{{
  "items": [
    {{
      "id": "<checklist-item-id>",
      "result": "PASS" or "FAIL",
      "reason": "<brief explanation>"
    }},
    ...
  ]
}}

Rules:
- The field MUST be named "result".
- "result" MUST be exactly "PASS" or "FAIL" (uppercase).
- Do NOT invent extra fields.
- Do NOT wrap the JSON in code blocks.
- Do NOT output text before or after the JSON.
- If something is missing or unclear, mark it as "FAIL".
"""

    user_prompt = {
        "text_to_evaluate": text,
        "checklist": checklist
    }

    response = client.chat.completions.create(
        model=model_name,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(user_prompt)}
        ],
        temperature=0
    )

    parsed = json.loads(response.choices[0].message.content)

    return parsed
