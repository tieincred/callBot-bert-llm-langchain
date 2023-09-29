from pydub import AudioSegment
from pydub.silence import split_on_silence
import os

def process_audio_files(input_folder, output_folder, silence_thresh=-60):
    # Ensure the output directory exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Iterate over every file in the input folder
    for file_name in os.listdir(input_folder):
        file_path = os.path.join(input_folder, file_name)
        
        # Load the audio file
        audio = AudioSegment.from_wav(file_path)
        
        # Print duration before processing
        print(f"Duration of {file_name} before processing: {len(audio) / 1000.0} seconds")
        
        # Split audio where the silence is more than 500ms
        chunks = split_on_silence(audio, min_silence_len=500, silence_thresh=silence_thresh)
        
        # Concatenate the chunks to form the audio without long silences
        processed_audio = sum(chunks, AudioSegment.empty())
        
        # Speed up the audio 1.5x only if its length is more than 5 seconds
        # if len(processed_audio) > 5000:
        #     processed_audio = processed_audio.speedup(playback_speed=1)
        
        # Print duration after processing
        print(f"Duration of {file_name} after processing: {len(processed_audio) / 1000.0} seconds")
        
        # Save the processed audio
        out_path = os.path.join(output_folder, file_name)
        processed_audio.export(out_path, format="wav")


# Usage
input_folder = "/media/pixis-ubuntu-20/pixis/tausif_workspace/chatbot/chat_bot/chatbotv3/just1"
output_folder = "/media/pixis-ubuntu-20/pixis/tausif_workspace/chatbot/chat_bot/chatbotv3/fixes_audios"
process_audio_files(input_folder, output_folder)
