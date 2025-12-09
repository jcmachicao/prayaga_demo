import os
import gradio as gr
import json

from helpers.io_utils import load_instructions, load_checklist
from helpers.iter_logic import improve_and_evaluate, checklist_passed
from config import MAX_ITERATIONS

# Gradio Callback
def update_and_check(draft, history, instructions, checklist_str):
    checklist = json.loads(checklist_str)
    prev = None
    history = history or []

    for i in range(MAX_ITERATIONS):
        improved, eval_json = improve_and_evaluate(instructions, checklist, draft, prev)
        prev = improved

        # ✔ Chatbot message format (v3)
        history.append({
            "role": "assistant",
            "content": f"**Iteration {i+1} – Updated Text:**\n\n{improved}"
        })

        history.append({
            "role": "assistant",
            "content": f"**Evaluation JSON:**\n```json\n{json.dumps(eval_json, indent=2)}\n```"
        })

        if checklist_passed(eval_json):
            history.append({
                "role": "system",
                "content": "Checklist passed — awaiting user approval."
            })
            break

        draft = improved

    # Outputs: chatbot history, improved draft, evaluation JSON formatted string
    return history, prev, json.dumps(eval_json, indent=2)


def approve(final_text, eval_str, approved):
    approved_bool = False
    if isinstance(approved, bool):
        approved_bool = approved
    else:
        approved_bool = str(approved).strip().lower() in ["true", "1", "yes", "on"]

    if not approved_bool:
        return "Please check 'Approve' to continue.", False

    try:
        eval_json = json.loads(eval_str)
    except Exception as e:
        return f"Cannot approve — evaluation is missing or invalid ({e}).", False

    try:
        if not checklist_passed(eval_json):
            return "Cannot approve — checklist not satisfied. Please complete all items.", False
    except Exception as e:
        return f"Cannot approve — checklist error ({e}).", False

    return "Approved successfully!", True

def build_ui():
    with gr.Blocks() as demo:
        # Main row
        with gr.Row():
            # Left column: input
            with gr.Column(scale=1, min_width=200):
                prompt_input = gr.Textbox(
                    label="Prompt", 
                    value="", 
                    lines=3, 
                    placeholder="Type your prompt here..."
                )
                submit_button = gr.Button(
                    value="Submit",  # 'value' must be string
                    elem_id="submit_button"  # optional, must be string
                )

            # Right column: output
            with gr.Column(scale=2, min_width=400):
                output_text = gr.Textbox(
                    label="Output", 
                    value="", 
                    lines=10, 
                    interactive=False
                )

        # Connect button to update output
        submit_button.click(
            fn=lambda prompt: f"Echo: {prompt}",  # replace with your actual function
            inputs=prompt_input,
            outputs=output_text
        )

    return demo

demo = build_ui()

if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 8000))
    demo.launch(server_name="0.0.0.0", server_port=PORT, share=True)  # or share=True
