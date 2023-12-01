from utils.embedding_calculate import transcript
from utils.node_bert_wlogger import TalkNode
from utils.key_word_list import correction_word
import gradio as gr
import time


def chatbot_conversation(input_text, current_node = None, wrongclass=False, most_probable_categories=None, node_stack=None, audio_stack=None):
    # Initialize the chatbot nodes
    start_node = TalkNode('Start Node')
    node2 = TalkNode('Node 2')
    node3 = TalkNode('Node 3')
    node4 = TalkNode('Node 4')
    node5 = TalkNode('Node 5')
    node6 = TalkNode('Node 6')
    node7 = TalkNode('Node 7')
    node8 = TalkNode('Node 8')
    node9 = TalkNode('Node 9')
    invoice_node = TalkNode('Invoice')
    node_undel = TalkNode('Undelivered Order Node')
    node_exchange = TalkNode('Exchange Order Node')
    end_node = TalkNode('End Node')


    # Set up the relationships between nodes
    end_node.set_up(None, ['end'], ['audio21.wav'], end_node=True)
    node9.set_up([end_node], ['replace', correction_word], ['audio20.wav', 'audio20.wav'])
    node8.set_up([node2, end_node], ['yes', 'no', correction_word], ['audio2.wav','audio17.wav', 'audio2.wav'])
    node7.set_up([node8, node8], ['amazon pay balance','source account', correction_word], ['audio10.wav', 'audio14.wav', 'audio10.wav'])
    node6.set_up([node7, node9], ['yes', 'replace', correction_word], ['audio9.wav', 'audio13.wav', 'audio9.wav'])
    node_undel.set_up([end_node], ['situation', correction_word], ['audio18.wav', 'audio18.wav'])
    node_exchange.set_up([end_node], ['reason', correction_word], ['audio19.wav', 'audio19.wav'])
    node5.set_up([node6, node_undel, node_exchange], ["return", "undelivered", "exchange", correction_word], ['audio8.wav', 'audio16.wav', 'audio15.wav', 'audio8.wav'])
    node4.set_up([node5, node3], ['yes', 'no', correction_word], ['audio7.wav', 'audio12.wav'])
    node3.set_up([node4], ['1', '2', '3', correction_word], ['audio4.wav', 'audio5.wav', 'audio6.wav'])
    invoice_node.set_up([node8, node8, correction_word], ['bill paid', 'order placed'], ['bill_paid.wav', 'order_placed.wav'])
    node2.set_up([node3, invoice_node], ['ordered Item', 'invoice', correction_word], ['audio3.wav', 'audio3.wav'])
    start_node.set_up([node4, node2], ['yes', 'no', correction_word], ['audio4.wav','audio2.wav'])
    if current_node == None:
        current_node = start_node
    # to calculate response time
    start_time = time.time()
    # Process the user input and get the next node and audio path
    next_node, audio_path, wrongclass, most_probable_categories, node_stack, audio_stack = current_node.process_text(input_text, wrongclass, most_probable_categories, node_stack, audio_stack)
    end_time = time.time()
    print(f"Response time: {end_time-start_time} seconds")
    # Return the next node and audio path
    return next_node, audio_path, wrongclass, most_probable_categories, node_stack, audio_stack

# Set the initial current node
current_node = None
wrongclass = False
most_probable_categories = None
# Stack to keep track of conversation nodes
node_stack = []
audio_stack = []


def reset_talkbot():
    global current_node, wrongclass, most_probable_categories, node_stack, audio_stack
    current_node = None
    wrongclass = False
    most_probable_categories = None
    node_stack.clear()
    audio_stack.clear()



def gradio_interface2_1(input_text):
    global current_node
    global wrongclass
    global most_probable_categories
    global node_stack
    global audio_stack
    if input_text.lower() == 'start':
        reset_talkbot()
        print(transcript('audios/audio1.wav'))
        return 'audios/audio1.wav'
    print('before hitting:', wrongclass)
    next_node, audio_data, wrongclass, most_probable_categories, node_stack, audio_stack = chatbot_conversation(input_text, current_node, wrongclass, most_probable_categories, node_stack, audio_stack)
    
    print('after hitting:', wrongclass)
    current_node = next_node
    if current_node is None:  # Check if the current node is None (i.e., end node)
        print("Conversation ended.")
        # print(transcript(audio_data))
        return audio_data  # Return the audio data from the end node
    # print(transcript(audio_data))
    print("****************Talk one done!!****************")
    return audio_data


def gradio_interface2_1(input_text=None, input_audio=None):
    global current_node
    global wrongclass
    global most_probable_categories
    global node_stack
    global audio_stack
    print(input_audio)
    # Determine the type of input and possibly transcribe it
    if input_audio:
        user_input = transcript(input_audio)
    else:
        user_input = input_text
    
    if user_input.lower() == 'start':
        reset_talkbot()
        return 'audios/audio1.wav'

    next_node, audio_data, wrongclass, most_probable_categories, node_stack, audio_stack = chatbot_conversation(user_input, current_node, wrongclass, most_probable_categories, node_stack, audio_stack)
    
    current_node = next_node
    if current_node is None:
        return audio_data
    
    return audio_data

# Gradio interface setup
input_components = [
    gr.inputs.Textbox(lines=2, label="User Input"),
    gr.inputs.Audio(source='microphone', label="User Audio Input", type='filepath', streaming=True)
]

output_audio = gr.outputs.Audio(type="filepath", label="Audio Response")

gr.Interface(fn=gradio_interface2_1, inputs=input_components, outputs=output_audio).launch(share=True)


# input_text = gr.inputs.Textbox(lines=2, label="User Input")
# output_audio = gr.outputs.Audio(type="filepath", label="Audio Response")
# gr.Interface(fn=gradio_interface2_1, inputs=input_text, outputs=output_audio).launch(share=True)