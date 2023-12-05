import webrtcvad
import pyaudio
import sys
import time
import noisereduce as nr
import numpy as np
import wave
from uuid import uuid4

# def check_time



def vad_and_save():
    print("Voice Activity Monitoring")
    print("1 - Activity Detected")
    print("_ - No Activity Detected")
    print("X - No Activity Detected for Last IDLE_TIME Seconds")
    # input("Press Enter to continue...")
    print("\nMonitor Voice Activity Below:")

    # Parameters
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000 # 8000, 16000, 32000
    FRAMES_PER_BUFFER = 320

    # Initialize the VAD with a mode (e.g. aggressive, moderate, or gentle)
    vad = webrtcvad.Vad(3)

    # Open a PyAudio stream to get audio data from the microphone
    pa = pyaudio.PyAudio()
    stream = pa.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=FRAMES_PER_BUFFER)

    # inactive_session = False
    # inactive_since = time.time()
    frames = [] # list to hold audio frames
    # Parameters
    SILENCE_THRESHOLD_PERCENTAGE = 70  # 70% silence in the buffer to consider it silent
    BUFFER_LENGTH = int(RATE * 1 / FRAMES_PER_BUFFER)  # Buffer length for 1 second
    # Initialize buffer
    silence_buffer = [0]*BUFFER_LENGTH
    while True:
        # Read audio data from the microphone
        data = stream.read(FRAMES_PER_BUFFER)
        
        # Convert data to an array for processing
        audio_data_array = np.fromstring(data, dtype=np.int16)

        # Apply noise reduction
        reduced_noise_data = nr.reduce_noise(y=audio_data_array, sr=RATE)

        # Convert back to bytes for VAD
        data = reduced_noise_data.tobytes()
        # Check if the audio is active (i.e. contains speech)
        is_active = vad.is_speech(data, sample_rate=RATE)
        
        silence_buffer.append(0 if is_active else 1)

        # Keep buffer length constant
        if len(silence_buffer) > BUFFER_LENGTH:
            silence_buffer.pop(0)

        # Calculate silence percentage
        silence_percentage = 100 * sum(silence_buffer) / len(silence_buffer)
        # Check Flagging for Stop after N Seconds
        # idle_time = 1
        # if is_active:
        #     inactive_session = False
        # else:
        #     if inactive_session == False:
        #         inactive_session = True
        #         inactive_since = time.time()
        #     else:
        #         inactive_session = True

        # Stop hearing if no voice activity detected for N Seconds
        # if (inactive_session == True) and (time.time() - inactive_since) > idle_time:
        if silence_percentage >= SILENCE_THRESHOLD_PERCENTAGE:
            sys.stdout.write('X')
            
            # Append data chunk of audio to frames - save later
            frames.append(data)

            # Save the recorded data as a WAV file
            audio_recorded_filename = f'recorded_audio\\RECORDED-{str(time.time())}-{str(uuid4()).replace("-","")}.wav'
            wf = wave.open(audio_recorded_filename, 'wb')
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(pa.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
            wf.close()

            # # Stop Debug
            # break

            # Some Sample Activity - 5 Seconds execution
            # time.sleep(5)
            # inactive_session = False
            return audio_recorded_filename
        else:
            sys.stdout.write('1' if is_active else '_')
        
        # Append data chunk of audio to frames - save later
        frames.append(data)

        # Flush Terminal
        sys.stdout.flush()

# # Parameters
# SILENCE_THRESHOLD_PERCENTAGE = 70  # 70% silence in the buffer to consider it silent
# BUFFER_LENGTH = int(RATE * 1 / FRAMES_PER_BUFFER)  # Buffer length for 1 second

# # Initialize buffer
# silence_buffer = []

# while True:
#     data = stream.read(FRAMES_PER_BUFFER)
#     is_active = vad.is_speech(data, RATE)

#     # Update buffer (1 for speech, 0 for silence)
#     silence_buffer.append(0 if is_active else 1)
    
#     # Keep buffer length constant
#     if len(silence_buffer) > BUFFER_LENGTH:
#         silence_buffer.pop(0)

#     # Calculate silence percentage
#     silence_percentage = 100 * sum(silence_buffer) / len(silence_buffer)

#     # Check if silence percentage meets the threshold
#     if silence_percentage >= SILENCE_THRESHOLD_PERCENTAGE:
#         # Code to execute when silence is detected
#         ...
#     else:
#         # Code to execute when speech is detected
#         ...

#     # Rest of your loop


# Close the PyAudio stream
# stream.stop_stream()


if __name__ == '__main__':
    print(vad_and_save())
