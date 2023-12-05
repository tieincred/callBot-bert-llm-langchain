from utils.embedding_calculate import transcript
from utils.node_bert_wlogger import TalkNode
from utils.key_word_list import correction_word
from call_api import get_audio
from vad import vad_and_save
from speakout import play_audio
import gradio as gr
import time
import os


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
    
    # account management nodes
    account_manage = TalkNode('account manage')
    payments_node = TalkNode('payments')
    gift_node = TalkNode('Gifts')
    
    # gift node
    gift_cancel_buy = TalkNode('Gift Transaction')

    # Invoice nodes
    invoice_node = TalkNode('Invoice')
    warranty_node = TalkNode('Warranty')
    node_undel = TalkNode('Undelivered Order')
    node_exchange = TalkNode('Exchange Order')
    end_node = TalkNode('End')

    # Prime membership 
    prime_member_node = TalkNode('Prime member')
    prime_member_cancel = TalkNode('prime cancel')
    prime_member_upgrade = TalkNode('prime upgrade')
    not_happy_node = TalkNode('Unhappy')
    expensive_node = TalkNode('Too expensive')

    end_node.set_up([None], ['end'], ['audio21.wav'], end_node=True)
    node9.set_up([end_node], ['replace'], ['audio20.wav', 'audio20.wav'])
    node8.set_up([node2, end_node], ['yes', 'no'], ['audio2.wav','audio17.wav', 'audio2.wav'])
    node7.set_up([node8, node8], ['amazon pay balance','source account'], ['audio10.wav', 'audio14.wav', 'audio10.wav'])
    node6.set_up([node7, node9], ['yes', 'replace'], ['audio9.wav', 'audio13.wav', 'audio9.wav'])
    node_undel.set_up([end_node], ['situation'], ['audio18.wav', 'audio18.wav'])
    node_exchange.set_up([end_node], ['reason'], ['audio19.wav', 'audio19.wav'])
    node5.set_up([node6, node_undel, node_exchange], ["return", "undelivered", "exchange"], ['audio8.wav', 'audio16.wav', 'audio15.wav', 'audio8.wav'])
    node4.set_up([node5, node3], ['yes', 'no'], ['audio7.wav', 'audio12.wav'])
    node3.set_up([node4], ['1', '2', '3'], ['audio4.wav', 'audio5.wav', 'audio6.wav'])
    gift_cancel_buy.set_up([node8, node8], ['buy', 'cancel'],['gift_buy.wav', 'gift_cancel.wav'])
    gift_node.set_up([node8,node8,gift_cancel_buy], ['add gift card', 'check balance', 'transaction'], ['gift_add.wav', 'check_balance.wav', 'gift_buy_cancel.wav'])
    payments_node.set_up([node8, node8], ['wallet', 'cash'], ['payments_wallet.wav', 'payments_cash.wav'])
    account_manage.set_up([node8, payments_node, gift_node], ['security and login', 'payments', 'gift card'], ["security.wav","payments.wav","gift.wav"])
    warranty_node.set_up([node8, node8], ['yes', 'no'], ['warranty.wav', 'warranty_direction.wav'])
    invoice_node.set_up([node8, node8], ['bill paid', 'order placed'], ['bill_paid.wav', 'order_placed.wav'])
    not_happy_node.set_up([node8, node8], ['yes', 'no'], ['yes_cancel.wav', 'no_cancel.wav'])
    expensive_node.set_up([node8, node8], ['yes', 'no'], ['yes_cancel.wav', 'no_cancel.wav'])
    prime_member_cancel.set_up([not_happy_node, expensive_node, node8], ['uphappy', 'expensive', 'something else'], ['unhappy.wav', 'expensive.wav', 'else.wav'])
    prime_member_upgrade.set_up([node8, node8], ['yes', 'no'], ['yes_upgrade.wav', 'no_upgrade.wav'])
    prime_member_node.set_up([prime_member_cancel, prime_member_upgrade], ['cancel','upgrade'], ['cancel_prime.wav', 'upgrade_prime.wav'])
    node2.set_up([node3, invoice_node, warranty_node, node8, node8, account_manage, prime_member_node], ['order', 'invoice', 'warranty', 'KYC', 'Deals and offers', 'account management', 'prime membership'], ['audio3.wav', 'invoice.wav', 'warranty.wav', 'kyc.wav', 'deals.wav', 'account.wav', 'prime.wav'])
    node2.classify_current = True
    start_node.set_up([node4, node2], ['yes', 'no'], ['audio4.wav','audio2.wav'])
    start_node.classify_current = True
    if current_node == None:
        current_node = start_node
    # to calculate response time
    start_time = time.time()
    # Process the user input and get the next node and audio path
    next_node, audio_path, wrongclass, most_probable_categories, node_stack, audio_stack = current_node.process_text(input_text, wrongclass, most_probable_categories, node_stack, audio_stack)
    end_time = time.time()
    response_time = end_time-start_time
    print(f"Response time: {end_time-start_time} seconds")
    return next_node, audio_path, wrongclass, most_probable_categories, node_stack, audio_stack, response_time




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



def gradio_interface2_2(input_text):
    global current_node
    global wrongclass
    global most_probable_categories
    global node_stack
    global audio_stack
    if input_text.lower() == 'start':
        # to generate personalised audio
        get_audio()
        reset_talkbot()
        print(transcript('audios/audio1.wav'))
        return 'audios/audio1.wav'
    print('before hitting:', wrongclass)
    next_node, audio_data, wrongclass, most_probable_categories, node_stack, audio_stack, response_time = chatbot_conversation(input_text, current_node, wrongclass, most_probable_categories, node_stack, audio_stack)
    
    print('after hitting:', wrongclass)
    current_node = next_node
    if current_node is None:  # Check if the current node is None (i.e., end node)
        print("Conversation ended.")
        # print(transcript(audio_data))
        return audio_data  # Return the audio data from the end node
    # print(transcript(audio_data))
    print("****************Talk one done!!****************")
    return audio_data, response_time


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
        # to generate personalised audio
        res_start = time.time()
        get_audio()
        reset_talkbot()
        res_end = time.time()
        response_time = res_end - res_start
        return 'audios/audio1.wav', 'final_individual_graphs/start_node_final.png', response_time

    next_node, audio_data, wrongclass, most_probable_categories, node_stack, audio_stack, response_time = chatbot_conversation(user_input, current_node, wrongclass, most_probable_categories, node_stack, audio_stack)
    if next_node:
        graph_image_path = f"final_individual_graphs/{next_node.node_name.replace(' ', '_').lower()}_node_final.png"
        if not os.path.exists(graph_image_path):
                graph_image_path = f"final_individual_graphs/{next_node.node_name.replace(' ', '_').lower()}_final.png"
    else:
        graph_image_path = "final_individual_graphs/end_node_final.png"
    current_node = next_node
    if current_node is None:
        return audio_data, graph_image_path, response_time
    
    return audio_data, graph_image_path, response_time

if __name__ == "__main__":
    input_user = input("Type start and press enter to start: ")
    file_path, _, _ = gradio_interface2_1(input_user)
    play_audio(file_path)
    while True:
        user_input = vad_and_save()
        file_path, _, _ = gradio_interface2_1(input_audio=user_input)
        play_audio(file_path)
        print("Bot: ",transcript(file_path))