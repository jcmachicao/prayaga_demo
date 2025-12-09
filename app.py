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


# Build UI
def build_ui():
    instructions = load_instructions()
    checklist = load_checklist()

    with gr.Blocks() as demo:
        with gr.Row():
            with gr.Column():
                instructions_box = gr.Textbox(value=instructions, label="Instructions")
                checklist_box = gr.Textbox(value=json.dumps(checklist, indent=2), label="Checklist JSON")

            with gr.Column():
                chat_state = gr.State([])
                chat_display = gr.Chatbot(label="Iterations")
                draft = gr.Textbox(label="Your draft")

                update_btn = gr.Button("Update and Check my Content")
                approve_chk = gr.Checkbox(label="Approve")
                approve_btn = gr.Button("Approve Final Text")

                eval_box = gr.Textbox(label="Evaluation JSON")

            with gr.Column():
                improved_text = gr.Textbox(label="Improved Text", lines=20)
                status = gr.Textbox(label="Status")

        update_btn.click(
            update_and_check,
            inputs=[draft, chat_state, instructions_box, checklist_box],
            outputs=[chat_display, improved_text, eval_box],
        )

        approve_btn.click(
            approve,
            inputs=[improved_text, eval_box, approve_chk],
            outputs=[status, approve_chk],
        )

    return demo


# Define Gradio interface
demo = build_ui()

if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 8000))  # Render provides PORT
    demo.launch(server_name="0.0.0.0", server_port=PORT, share=True)

