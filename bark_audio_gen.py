from transformers import AutoProcessor, BarkModel
import torch
import scipy
import os
import time
from utils.embedding_calculate import transcript
from tqdm import tqdm

os.environ['SUNO_USE_SMALL_MODELS'] = 'True'

device = "cuda" if torch.cuda.is_available() else "cpu"
processor = AutoProcessor.from_pretrained("suno/bark")
optimised = True

if not optimised:
    start = time.time()
    model = BarkModel.from_pretrained("suno/bark").to(device)
    model = model.to_bettertransformer()

else:
    start = time.time()
    # load in fp16
    model = BarkModel.from_pretrained("suno/bark-small", torch_dtype=torch.float16).to(device)

    # convert to bettertransformer
    model = model.to_bettertransformer()

    # enable CPU offload
    model.enable_cpu_offload()


voice_preset = "v2/en_speaker_9"



def generate_audio(text, voice_preset, processor, model, out_name):
    # Start timing
    start = time.time()

    # Generate audio inputs using the processor
    inputs = processor(text, voice_preset=voice_preset)

    # Generate audio using the model
    audio_array = model.generate(**inputs.to(device))
    audio_array = audio_array.cpu().numpy().squeeze()

    # Calculate generation time
    gen_time = time.time()

    # Write audio to file
    sample_rate = model.generation_config.sample_rate
    scipy.io.wavfile.write(out_name, rate=sample_rate, data=audio_array)

    # Calculate total time
    done_time = time.time()
    total_time = done_time - start

    # Return the generated audio array and the generation time
    return audio_array, gen_time, total_time

# generate_audio('text', voice_preset, processor, model, f'new_audio.wav')

import json

def generate_audios_from_transcriptions(json_path, output_folder):
    # Load transcriptions from the JSON file
    with open(json_path, 'r') as f:
        transcriptions = json.load(f)

    # For each transcription, generate audio and save it
    for file_name, text in tqdm(transcriptions.items()):
        out_name = os.path.join(output_folder, f"{os.path.splitext(file_name)[0]}.wav")
        if not os.path.exists(out_name):
            generate_audio(text, voice_preset, processor, model, out_name)

start = time.time()
generate_audio("So, you want help with an Item you ordered right?", voice_preset, processor, model, 'audio3.wav')
end = time.time()

print(f"time taken: {end-start} seconds.")
# Example usage
json_path = "transcription.json"
output_folder = "new_audios"
generate_audios_from_transcriptions(json_path, output_folder)

# files = os.listdir('audios')
# for audio_file in tqdm(files):
#     aud_path = os.path.join('audios', audio_file)
#     text = transcript(aud_path)
#     print(text)
#     audio, gen_time, total_time = 
#     print(f'total time {total_time}')
#     print(f'generation time {gen_time - start}')
