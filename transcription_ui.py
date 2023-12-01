from utils.embedding_calculate import transcript
# import gradio as gr

# def transcribe(audio, state=""):
#     # time.sleep(3)
#     print('audio: ',audio)
#     text = 'p(audio)["text"]'
#     state += text + " "
#     return state, state

# # # Gradio interface setup
# # input_components = [
# #     gr.inputs.Textbox(lines=2, label="User Input"),
# #     gr.inputs.Audio(source='microphone', label="User Audio Input", type='filepath')
# # ]

# # output_audio = gr.outputs.Textbox(label="Audio Response")

# # gr.Interface(fn=transcribe, inputs=input_components, outputs=output_audio, live=True).launch(share=True)
# gr.Interface(
#     fn=transcribe,
#     inputs=[
#         gr.Audio(type="filepath"),  # Adjusted this line
#         'state'
#     ],
#     outputs=[
#         "textbox",
#         "state"
#     ],
#     live=True
# ).launch()

import gradio as gr
from transformers import pipeline
import numpy as np

transcriber = pipeline("automatic-speech-recognition", model="openai/whisper-base.en")

def transcribe(stream, new_chunk):
    sr, y = new_chunk
    y = y.mean(axis=1) 
    y = y.astype(np.float32)
    y /= np.max(np.abs(y))

    if stream is not None:
        stream = np.concatenate([stream, y])
    else:
        stream = y
    return stream, transcript(y)


demo = gr.Interface(
    transcribe,
    ["state", gr.Audio(source="microphone", streaming=True)],
    ["state", "text"],
    live=True,
)

demo.launch()
