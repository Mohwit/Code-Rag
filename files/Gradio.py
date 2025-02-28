import test51
import test50
import test_5
PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0

import text_3
import test_2
import test_4
import test_10
import pip
import os
import gradio as gr

# Set default port safely
PORT = int(os.environ.get("PORT", 7860))
def generate_summary(input_text):
    output = summarize_text(input_text)
    print("HELLO")
    return output

def generate_summary(input_text):
    output = summarize_text(input_text)
    print(output)
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
import test
import pip
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
