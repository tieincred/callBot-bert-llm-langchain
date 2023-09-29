import logging
from utils.embedding_calculate import *
from utils.key_word_list import list_of_words, correction_word
from utils.constants import *
from transformers import pipeline
import time

curr_time = time.time()
file_name = 'logs/'+ str(curr_time) + '.txt'
# Configure logging
logging.basicConfig(filename=file_name, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli", device=0)
with open('utils/nodeClasses.json', 'r') as f:
    # Load the JSON content from the file
    node_classes = json.load(f)
# classifier = pipeline("zero-shot-classification", model="distilbert-base-uncased")

class TalkNode:
    def __init__(self, name):
        self.next_nodes = None
        self.categories = None
        self.categories_audio = None
        self.check_function = None
        self.end_node = False
        self.text = ''
        self.node_name = name
        self.classify_current = False

    def set_up(self, next_nodes, categories, categories_audio, check_function=None, end_node=False):
        self.next_nodes = next_nodes
        self.categories = categories
        self.categories_audio = categories_audio
        self.check_function = check_function
        self.end_node = end_node

    def get_audio_path(self, most_probable_category_id):
        logging.info('Getting audio path for category ID: %s', most_probable_category_id)
        if most_probable_category_id == correction_word:
            return 'audios/audio_wrong.wav'
        return 'audios/' + self.categories_audio[most_probable_category_id]

    def handle_end_node(self, node_stack, audio_stack):
        logging.info("Reached end node.")
        audio_path = self.get_audio_path(0)
        logging.info("Audio Path: %s", audio_path)
        return None, audio_path, False, node_stack, audio_stack

    def handle_wrong_classification(self, most_probable_category, wrong_class, node_stack, audio_stack):
        logging.info('Wrong classification reported.')
        if not most_probable_category:
            audio_path = self.get_audio_path(correction_word)
            next_node = self
        else:
            if wrong_class:
                logging.info('Consequently wrong again! Staying at the current node')
                next_node = self  # Stay on the current node
                audio_path = audio_stack.pop()
            elif node_stack:
                logging.info('Reverting to the previous node')
                node_stack.pop()
                audio_stack.pop()
                audio_path = audio_stack.pop()
                next_node = node_stack.pop()  # Pop the current node to revert to the previous node
                logging.info(f'Reverting from {self.node_name} to {next_node.node_name}')
            else:
                logging.info('No previous node to revert to. Staying at the current node')
                next_node = self  # Stay on the current node if stack is empty
                audio_path = audio_stack.pop()
        return next_node, audio_path, True, node_stack, audio_stack

    def most_probable_id(self, most_probable_category):
        most_probable_category_id = self.categories.index(most_probable_category)
        return most_probable_category_id

    def find_first_index_less_than_threshold(self, sorted_list, threshold=0.3):
        low, high = 0, len(sorted_list) - 1
        
        while low <= high:
            mid = (low + high) // 2
            if sorted_list[mid] < threshold:
                if mid == 0 or sorted_list[mid - 1] >= threshold:
                    return mid
                high = mid - 1
            else:
                low = mid + 1
        
        return 0
    
    def update_candidate_labels(self, most_probable_categories):
        list_of_words_present = list_of_words.copy()
        for cat in most_probable_categories:
            if cat in list_of_words:
                list_of_words_present.remove(cat)
        return list_of_words_present
    

    def get_most_probable_with_bert(self, sentence, most_probable_categories):
        # here most_probable_categories are basically already found classes, name's that to save convention throughout the code.
        if 'no' in self.categories:
            CORRECTION_CONFIDENCE = CORRECTION_CONFIDENCE_THRESHOLD_WHEN_NO
        else:
            CORRECTION_CONFIDENCE = CORRECTION_CONFIDENCE_THRESHOLD
        logging.info("==============*************===============")
        logging.info(f"The correction confidence is {CORRECTION_CONFIDENCE_THRESHOLD}")
        logging.info('Using Bert to find the most probable category!!')
        logging.info("Incoming sentence: %s", sentence)

        if sentence == '':
            logging.warning("Received an empty sentence!")
            return []

        logging.info("Incoming classes: %s", list_of_words)
        list_of_words_present = node_classes[self.node_name]
        if most_probable_categories:
            list_of_words_present = self.update_candidate_labels(most_probable_categories)
        if self.classify_current:
            result = classifier(sentence, candidate_labels=self.categories, multi_class=True)
        else:
            result = classifier(sentence, candidate_labels=list_of_words_present, multi_class=True)
        logging.info("===== LABELS AND SCORES =====")
        logging.info(result['labels'][:5])
        logging.info(result['scores'][:5])

        idx = self.find_first_index_less_than_threshold(result['scores'], FIRST_DETECTION_CONFIDENCE)
        if idx == 0:
            idx = self.find_first_index_less_than_threshold(result['scores'], SECOND_DETECTION_CONFIDENCE)
            if idx == 0:
                idx = 1
        logging.info("Selected index based on threshold: %d", idx)

        # Check for the correction_word and its confidence
        filtered_labels = []
        correction_word_score = None
        for label, score in zip(result['labels'][:idx], result['scores'][:idx]):
            if label == correction_word:
                correction_word_score = score
                logging.info("Found correction_word with score: %f", score)
                if score <= CORRECTION_CONSIDERATION_THRESHOLD:
                    logging.info("Ignoring correction_word due to its low confidence score.")
                    continue
            else:
                filtered_labels.append(label)

        # if correction_word not in filtered_labels:
        #     logging.info("correction_word not found in filtered labels. Returning early.")
        #     return filtered_labels

        # correction_word should pass a minimum difference and unique threshold to be accounted for.
        # import pdb
        # pdb.set_trace()
        max_other_score = max([score for label, score in zip(result['labels'], result['scores']) if label != correction_word], default=0)
        logging.info("Max score from other labels: %f", max_other_score)

        if correction_word_score and (correction_word_score - max_other_score > CORRECTION_CONFIDENCE):
            logging.info("Difference between correction_word score and max other score is above the threshold.")
            if not any(score > OTHER_CLASS_MIN_THRESH_WITH_CORRECTION for score,label in zip(result['scores'],result['labels']) if label != correction_word):
                logging.info("No label has a score greater than the threshold, so adding correction_word to the list.")
                filtered_labels.append(correction_word)
        else:
            logging.warning("Either correction_word was not found or its score difference with max other score is below the threshold.")

        logging.info("Final filtered labels: %s", filtered_labels)
        logging.info("==============*************===============")
        return filtered_labels

    
    def handle_general_conversation(self, most_probable_category, wrong_class, node_stack, audio_stack):
        most_probable_category_id = self.most_probable_id(most_probable_category)
        
        if self.categories[most_probable_category_id] == correction_word:
            most_probable_category = correction_word
            return self.handle_wrong_classification(most_probable_category, wrong_class, node_stack, audio_stack)
        
        audio_path = self.get_audio_path(most_probable_category_id)
        if self.next_nodes:
            try:
                next_node = self.next_nodes[most_probable_category_id]
            except:
                next_node = self.next_nodes[0]
        else:
            next_node = None
        return next_node, audio_path, False, node_stack, audio_stack
    
    def get_current_cat(self, most_probable_categories):
        if correction_word == most_probable_categories[0]:
            return correction_word, [correction_word]
        logging.info('=======> to check from: %s', self.categories)
        for category in self.categories:
            logging.info('Checking for: %s in %s', category, most_probable_categories)
            if category in most_probable_categories:
                most_probable_categories.remove(category)
                return category, most_probable_categories
        
        return None, most_probable_categories
    
    def get_next_cat(self, most_probable_categories, check_cats):
        if correction_word in most_probable_categories:
            return correction_word
        for category in check_cats:
            if category in most_probable_categories:
                return category
        return None
    
    def get_response_and_node_info(self, most_probable_category, wrong_class=False, node_stack=None, audio_stack=None):
        if self.end_node == True:
            return self.handle_end_node(node_stack, audio_stack)
        
        if not self.check_function:
            if most_probable_category in [None, correction_word]:
                return self.handle_wrong_classification(most_probable_category, wrong_class, node_stack, audio_stack)
        
        return self.handle_general_conversation(most_probable_category, wrong_class, node_stack, audio_stack)

    def process_text(self, text, wrong_class=False, most_probable_categories=None, node_stack=None, audio_stack=None):
        logging.info("********************** NEW NODE ************************")
        logging.info(f"Processing text in node: {self.node_name}")
        logging.info(f"Input Text: {text}")
        logging.info(f"Already Found MPC: {most_probable_categories}")
        logging.info(f"Wrong Class: {wrong_class}")
        logging.info(f"Node Categories: {self.categories}")
        self.text = text
        node_stack.append(self)
        new_most_probable_categories = self.get_most_probable_with_bert(text, most_probable_categories)
        # removing correction_word from new_most_probable_categories if it's not most probable 
        if (correction_word in new_most_probable_categories) and (correction_word!=new_most_probable_categories[0]):
            new_most_probable_categories.remove(correction_word)

        logging.info(f'Most Probable categories found: {new_most_probable_categories}')
        logging.info(f"Already Found MPC: {most_probable_categories}")
        if most_probable_categories:
            most_probable_categories = new_most_probable_categories + most_probable_categories
        else:
            most_probable_categories = new_most_probable_categories
        most_probable_categories = list(set(most_probable_categories))
        logging.info(f'New Most Probable categories: {most_probable_categories}')

        if most_probable_categories[0] == correction_word:
            logging.info(f'Ah here is the correction word: {most_probable_categories[0]}')
            next_node, audio_path, wrong_class, node_stack, audio_stack = self.get_response_and_node_info(correction_word, wrong_class, node_stack, audio_stack)
            # bot_words = transcript(audio_path)
            # logging.info(f'Bot:  {bot_words}')
            audio_stack.append(audio_path)
            return next_node, audio_path, wrong_class, most_probable_categories, node_stack, audio_stack
        currently_use_category, most_probable_categories = self.get_current_cat(most_probable_categories)
        next_node, audio_path, wrong_class, node_stack, audio_stack = self.get_response_and_node_info(currently_use_category, wrong_class, node_stack, audio_stack)
        if next_node:
            next_cat_check = self.get_next_cat(most_probable_categories, next_node.categories)
            if next_cat_check and next_cat_check!=correction_word:
                logging.info(f'Found next node category calling Recursion with category {next_cat_check}')
                next_node, audio_path, wrong_class, most_probable_categories, node_stack, audio_stack = next_node.process_text('', wrong_class, most_probable_categories, node_stack, audio_stack)
        # bot_words = transcript(audio_path)
        # logging.info(f'Bot:  {bot_words}')
        audio_stack.append(audio_path)
        return next_node, audio_path, wrong_class, most_probable_categories, node_stack, audio_stack