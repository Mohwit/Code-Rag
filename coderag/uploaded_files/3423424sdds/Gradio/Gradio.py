import os
import gradio as gr

# Set default port safely
PORT = int(os.environ.get("PORT", 7860))

def generate_summary(input_text):
    output = summarize_text(input_text)
    return output

gr.close_all()
demo = gr.Interface(
    fn=generate_summary,
    inputs=[gr.Textbox(label="Text to summarize", lines=6)],
    outputs=[gr.Textbox(label="Summary", lines=3)],
    title="Text Summarization",
    description="Summarize text using a pre-trained model."
)

demo.launch(share=True, server_port=PORT)
