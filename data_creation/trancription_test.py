import os
import time
import json
import wave
from utils.embedding_calculate import transcript

def transcribe_folder(folder_path):
    # List all files in the specified folder
    all_files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    
    # Filter for .wav files
    audio_files = [f for f in all_files if f.endswith('.wav')]
    
    transcriptions = {}
    total_time = 0
    total_duration = 0
    
    for audio_file in audio_files:
        audio_path = os.path.join(folder_path, audio_file)
        print(audio_file)
        # Calculate transcription time
        start_time = time.time()
        transcribed_text = transcript(audio_path)
        end_time = time.time()
        
        transcriptions[audio_file] = transcribed_text
        
        # Calculate audio file duration
        with wave.open(audio_path, 'r') as f:
            frames = f.getnframes()
            rate = f.getframerate()
            duration = frames / float(rate)
            total_duration += duration

        # Print time taken for this file
        elapsed_time = end_time - start_time
        total_time += elapsed_time
        print(f"Time taken to transcribe {audio_file}: {elapsed_time:.2f} seconds")

    # Save transcriptions to JSON file
    with open('transcription.json', 'w') as json_file:
        json.dump(transcriptions, json_file)
    
    # Calculate average transcription time per 5 seconds of audio
    avg_time_per_5s = (total_time / total_duration) * 5
    print(f"Average transcription time per 5 seconds of audio: {avg_time_per_5s:.2f} seconds")

# Example usage
transcribe_folder('/media/pixis-ubuntu-20/pixis/tausif_workspace/chatbot/chat_bot/chatbotv3/audios')
