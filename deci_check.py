import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from time import time
import os
os. environ['TRANSFORMERS_CACHE'] = '/media/pixis-ubuntu-20/pixis/tausif_workspace/adgenpipe/chat_bot/chatbotv3/hf_cache'
print(os. getenv('TRANSFORMERS_CACHE'))
# checkpoint = "Deci/DeciLM-6b"
checkpoint = 'meta-llama/Llama-2-7b-chat-hf'
device = "cuda" # for GPU usage or "cpu" for CPU usage

tokenizer = AutoTokenizer.from_pretrained(checkpoint)
model = AutoModelForCausalLM.from_pretrained(checkpoint, torch_dtype=torch.bfloat16, trust_remote_code=True, cache_dir=os.environ['TRANSFORMERS_CACHE']).to(device)


# prompt = f'''Given the following human response, identify whether it indicates that the human feels they were misunderstood by providing a one-word answer: 'Yes' or 'No'.
# Response: "I believe there's been a mix-up. What I meant was..."
# Is this response indicates that the human feels they were misunderstood?
# please keep it one word either yes or no
# '''
prompt = '--'

while prompt!='':
    prompt = input('Prompt: ')
    max_token = int(input('Max tokens: '))
    max_time = int(input('Max Time: +'))
    start = time()
    inputs = tokenizer.encode(prompt, return_tensors="pt").to(device)
    outputs = model.generate(inputs, max_new_tokens=max_token, top_p=0.95, max_time=max_time)
    print(len(outputs))
    print(outputs)
    print(tokenizer.decode(outputs[0]))
    end = time()

    print(end-start)