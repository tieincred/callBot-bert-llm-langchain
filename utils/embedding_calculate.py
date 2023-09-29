import json
import torch
# import nltk
from transformers import BertModel, BertTokenizer
from faster_whisper import WhisperModel
# from nltk.corpus import stopwords

# Load NLTK stopwords
# nltk.download('stopwords')
# nltk.download('punkt')
# stopwords = set(stopwords.words('english'))

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")


transcript_model = WhisperModel("large-v2")
model_name = 'bert-base-uncased'
tokenizer = BertTokenizer.from_pretrained(model_name)
model = BertModel.from_pretrained(model_name).to(device)

def transcript(audio_path):
  transcription = ""
  segments, info = transcript_model.transcribe(audio_path, language='en')
  for segment in segments:
      transcription = transcription + segment.text
  return transcription

def embed(input_text):
  # tokenizer-> token_id
  input_ids = tokenizer.encode(input_text, add_special_tokens=True)
  # input_ids: [101, 2182, 2003, 2070, 3793, 2000, 4372, 16044, 102]
  input_ids = torch.tensor([input_ids])

  with torch.no_grad():
      last_hidden_states = model(input_ids)[0] # Models outputs are now tuples
  last_hidden_states = last_hidden_states.mean(1)
  return last_hidden_states[0]


def var2embed():
    # Load the JSON file
    with open('variations.json', 'r') as f:
        json_data = json.load(f)

    # Create a dictionary to store the embeddings
    embeddings_dict = {}

    # Preprocess the text
    def preprocess_text(text):
        # Tokenize the text
        return text

    # Iterate over the categories and rephrased sentences
    for category, data in json_data['sentences'].items():
        print(category)
        variations = data['variations']
        embeddings = []
        
        # Encode and store the embeddings for each rephrased sentence in the category
        for sentence in variations:
            # Preprocess the sentence
            preprocessed_sentence = preprocess_text(sentence)
            embedding = embed(preprocessed_sentence)
            
            embeddings.append(embedding)
        
        # Calculate the average embedding for the category
        category_average_embedding = torch.mean(torch.stack(embeddings), dim=0).tolist()
        
        embeddings_dict[category] = category_average_embedding

    # Save the embeddings to a JSON file
    with open('embeddings.json', 'w') as f:
        json.dump(embeddings_dict, f)


# var2embed()