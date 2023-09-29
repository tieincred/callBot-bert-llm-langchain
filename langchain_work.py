from langchain import PromptTemplate, HuggingFaceHub, LLMChain
from langchain.llms import HuggingFacePipeline
import torch
import time
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline, AutoModelForSeq2SeqLM

import os
os.environ['HUGGINGFACEHUB_API_TOKEN'] = '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'
os.environ['TRANSFORMERS_CACHE'] = '/media/pixis-ubuntu-20/pixis/tausif_workspace/adgenpipe/chat_bot/chatbotv3/hf_cache'

template = """Given the following human response, identify whether it indicates that the human feels they were misunderstood by providing a one-word answer: 'Yes' or 'No'.
Is this response indicates that the human feels they were misunderstood?
Response: {question}
please keep it one word either yes or no"""

prompt = PromptTemplate(template=template, input_variables=["question"])
api = False
if api:
    llm_chain = LLMChain(prompt=prompt, 
                        llm=HuggingFaceHub(repo_id="google/flan-t5-xl", 
                                            model_kwargs={"temperature":0, 
                                                        "max_length":64}))
else:
    # model_id = 'google/flan-t5-small'
    # tokenizer = AutoTokenizer.from_pretrained(model_id, cache_dir=os.environ['TRANSFORMERS_CACHE'])
    # model = AutoModelForSeq2SeqLM.from_pretrained(model_id, load_in_8bit=True, device_map='auto')

    checkpoint = 'Deci/DeciLM-6b'
    device = "cuda" # for GPU usage or "cpu" for CPU usage

    tokenizer = AutoTokenizer.from_pretrained(checkpoint)
    model = AutoModelForCausalLM.from_pretrained(checkpoint, torch_dtype=torch.bfloat16, trust_remote_code=True, cache_dir=os.environ['TRANSFORMERS_CACHE'], device_map='auto')

    pipeline = pipeline(
        "text-generation",
        model=model, 
        tokenizer=tokenizer, 
        max_length=128
    )

    local_llm = HuggingFacePipeline(pipeline=pipeline)
    llm_chain = LLMChain(prompt=prompt, 
                     llm=local_llm
                     )

question = "I believe there's been a mix-up. What I meant was..."
start = time.time()
print(llm_chain.run(question))
end = time.time()

print(end-start)