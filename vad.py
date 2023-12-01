import pyaudio
import numpy as np
import auditok

# Audio parameters
FORMAT = pyaudio.paInt32
CHANNELS = 1
RATE = 44100
CHUNK = 1024

# Initialize PyAudio
audio = pyaudio.PyAudio()

device_index = 20
# Open a stream for microphone input
stream = audio.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True,
                    frames_per_buffer=CHUNK, input_device_index=device_index)

# Custom data source class
class NumpyAudioSource:
    def __init__(self, stream, chunk_size):
        self.stream = stream
        self.chunk_size = chunk_size

    def read(self):
        data = self.stream.read(self.chunk_size)
        return np.frombuffer(data, dtype=np.int16)


# Validator function
# def my_validator(audio_chunk):
#     energy_threshold = 50
#     squared_mean = np.mean(np.square(audio_chunk))
#     if np.isnan(squared_mean) or squared_mean < 0:
#         print("Invalid squared mean value:", squared_mean)
#         return False
#     else:
#         return np.sqrt(squared_mean) > energy_threshold
#     return np.sqrt(np.mean(np.square(audio_chunk))) > energy_threshold

def my_validator(audio_chunk):
    energy_threshold = 50
    # audio_chunk = audio_chunk.astype(np.float32)  # Convert to float to avoid overflow
    squared_mean = np.mean(np.square(audio_chunk))
    if np.isnan(squared_mean) or squared_mean < 0:
        print("Invalid squared mean value:", squared_mean)
        return False
    else:
        print(np.sqrt(squared_mean))
        return np.sqrt(squared_mean) > energy_threshold

# Create an instance of the custom data source
numpy_audio_source = NumpyAudioSource(stream, CHUNK)

# Create an Auditok detector
detector = auditok.StreamTokenizer(validator=my_validator, min_length=100, max_length=500, max_continuous_silence=30)

# Process the audio stream
while True:
    try:
        regions = detector.tokenize(numpy_audio_source)
        print(regions)
        for r in regions:
            print("Detected speech: Start: {}, End: {}".format(r.meta.start, r.meta.end))
    except KeyboardInterrupt:
        break

# Stop and close the audio stream
stream.stop_stream()
stream.close()
audio.terminate()