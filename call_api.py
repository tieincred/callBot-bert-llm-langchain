import requests

# Set the URL of your Flask API
api_url = 'http://127.0.0.1:5000/process'

def get_audio():
    # Specify the key you want to pass
    key_to_send = 'example_key'

    # Make a GET request to the API with the key parameter
    response = requests.get(api_url, params={'key': key_to_send})

    # Check the response
    if response.status_code == 200:
        # The request was successful
        result = response.json()
        print(f"API Response: {result['result']}")
    else:
        # Handle errors
        print(f"Error: {response.status_code}, {response.text}")
