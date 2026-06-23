"""
Gradio Chat Interface — LLM Analytics Assistant
================================================
Run: python app.py
Then open: http://localhost:7860
"""
import os
import gradio as gr
from dotenv import load_dotenv
from assistant import ask

load_dotenv()

# Suggested starter questions shown in the UI
EXAMPLES = [
    "Give me an overview of our customer segments.",
    "How much revenue is at risk from churning customers?",
    "What was the worst KPI anomaly detected?",
    "Which 5 products have the biggest margin pricing opportunity?",
    "If I wanted to maximise revenue instead of margin, what changes?",
    "How accurate is the pricing model?",
    "Show me the top 10 customers by lifetime spend.",
    "Which product categories should I raise prices in?",
]

CSS = """
body { background: #191414 !important; }
.gradio-container { background: #191414 !important; font-family: 'Arimo', sans-serif !important; }
.chat-message.user .message { background: #4100F5 !important; color: white !important; border-radius: 12px !important; }
.chat-message.bot  .message { background: #1E1A1A !important; color: #F5F5F0 !important; border: 1px solid #2a2525 !important; border-radius: 12px !important; }
footer { display: none !important; }
"""

def respond(message, chat_history):
    history_pairs = [(h[0], h[1]) for h in chat_history]
    answer = ask(message, history=history_pairs)
    chat_history.append((message, answer))
    return "", chat_history

with gr.Blocks(css=CSS, title="Analytics Assistant — Klarissa Artavia") as demo:
    gr.HTML("""
    <div style="background:linear-gradient(135deg,#4100F5,#F037A5,#FF4632);padding:32px 40px;border-radius:12px;margin-bottom:24px;">
      <p style="font-family:'JetBrains Mono',monospace;font-size:11px;letter-spacing:0.25em;color:rgba(255,255,255,0.75);margin:0 0 10px;">
        LLM ANALYTICS ASSISTANT · KLARISSA ARTAVIA
      </p>
      <h1 style="font-size:28px;font-weight:900;color:#fff;margin:0 0 8px;letter-spacing:-0.03em;">
        Ask your data anything.
      </h1>
      <p style="color:rgba(255,255,255,0.8);margin:0;font-size:14px;">
        Natural language interface over customer segmentation, KPI monitoring, and dynamic pricing data.
        Powered by Claude + LangChain.
      </p>
    </div>
    """)

    chatbot = gr.Chatbot(height=480, show_label=False)
    msg     = gr.Textbox(
        placeholder="Ask about customers, KPI alerts, or pricing recommendations...",
        show_label=False,
        container=False,
    )
    with gr.Row():
        submit = gr.Button("Ask", variant="primary")
        clear  = gr.Button("Clear", variant="secondary")

    gr.HTML("<p style='color:#9E9A9A;font-size:12px;font-family:JetBrains Mono,monospace;margin-top:8px;'>EXAMPLE QUESTIONS</p>")
    gr.Examples(
        examples=EXAMPLES,
        inputs=msg,
        label="",
    )

    submit.click(respond, [msg, chatbot], [msg, chatbot])
    msg.submit(respond, [msg, chatbot], [msg, chatbot])
    clear.click(lambda: ([], ""), outputs=[chatbot, msg])

    gr.HTML("""
    <div style="margin-top:24px;padding-top:16px;border-top:1px solid #2a2525;text-align:center;">
      <p style="font-family:'JetBrains Mono',monospace;font-size:10px;letter-spacing:0.15em;color:#9E9A9A;text-transform:uppercase;">
        Built by <a href="https://www.linkedin.com/in/klariartavia/" style="color:#4100F5">Klarissa Artavia</a> ·
        <a href="https://github.com/klaricracia" style="color:#4100F5">github.com/klaricracia</a>
      </p>
    </div>
    """)

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_api=False,
    )
