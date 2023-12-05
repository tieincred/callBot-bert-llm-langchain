# import requests
# import base64
# import json
# # Set the URL of your Flask API
# api_url = 'https://3638-122-166-215-152.ngrok-free.app/process'

# def decode_and_save_audio(encoded_audio, output_path):
#     audio_data = base64.b64decode(encoded_audio)
#     with open(output_path, 'wb') as file:
#         file.write(audio_data)

# def get_audio():
#     # Specify the key you want to pass
#     key_to_send = 'example_key'

#     # Make a GET request to the API with the key parameter
#     response = requests.get(api_url, params={'key': key_to_send})

#     # Check the response
#     if response.status_code == 200:
#         # The request was successful
#         result = response.json()
#         print(f"API Response: {result}")
#     else:
#         # Handle errors
#         print(f"Error: {response.status_code}, {response.text}")

#     # Iterate through the received audio files and save them
#     for key, encoded_audio in response['audios'].items():
#         output_path = f"C:\\Users\\Piyush\\callBot-bert-llm-langchain\\audios\\{key}.wav"  # or any other path where you want to save the file
#         decode_and_save_audio(encoded_audio, output_path)

import requests
import base64

def decode_and_save_audio(encoded_audio, output_path):
    audio_data = base64.b64decode(encoded_audio)
    with open(output_path, 'wb') as file:
        file.write(audio_data)

def get_audio():
    api_url = 'https://3638-122-166-215-152.ngrok-free.app/process'

    # Specify the key you want to pass
    key_to_send = 'example_key'

    # Make a GET request to the API with the key parameter
    response = requests.get(api_url, params={'key': key_to_send})

    # Check the response
    if response.status_code == 200:
        # The request was successful
        result = response.json()
        print(f"API Response: {result}")

        # Iterate through the received audio files and save them
        for key, encoded_audio in result['audios'].items():
            # output_path = f"C:\\Users\\Piyush\\callBot-bert-llm-langchain\\audios\\{key}.wav" 
            output_path = f"{key}.wav"  # or any other path where you want to save the file
            decode_and_save_audio(encoded_audio, output_path)

    else:
        # Handle errors
        print(f"Error: {response.status_code}, {response.text}")






