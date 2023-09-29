from utils.embedding_calculate import *
from utils.key_word_list import list_of_words, correction_word
from transformers import pipeline
import sys



classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
# classifier = pipeline("zero-shot-classification", model="distilbert-base-uncased")

class TalkNode:
    def __init__(self, name):
        self.next_nodes = None
        self.prev_node = None
        self.categories = None
        self.categories_audio = None
        self.check_function = None
        self.end_node = False
        self.text = ''
        self.node_name = name

    def set_up(self, next_nodes, categories, categories_audio, check_function=None, end_node=False, prev_node=None):
        self.next_nodes = next_nodes
        self.categories = categories
        self.categories_audio = categories_audio
        self.check_function = check_function
        self.end_node = end_node
        self.prev_node = prev_node

    
    def get_audio_path(self, most_probable_category_id):
        print(most_probable_category_id)
        if most_probable_category_id == correction_word:
            return 'audios/audio_wrong.wav'
        return 'audios/'+self.categories_audio[most_probable_category_id]
    
    def handle_end_node(self, node_stack):
        print("Reached end node.")
        audio_path = self.get_audio_path(0)
        print("Audio Path:", audio_path)
        return None, audio_path, False, node_stack

    def handle_wrong_classification(self, most_probable_category, wrong_class, node_stack):
        print('Wrong classification reported.')
        audio_path = self.get_audio_path(most_probable_category)

        if wrong_class:
            print('Consequetively wrong again! Staying at the current node')
            next_node = self  # Stay on the current node
        elif node_stack:
            print('Reverting to the previous node')
            next_node = node_stack.pop()  # Pop the current node to revert to the previous node
        else:
            print('No previous node to revert to. Staying at the current node')
            next_node = self  # Stay on the current node if stack is empty

        return next_node, audio_path, True, node_stack


    def most_probable_id(self, most_probable_category):
        
        most_probable_category_id = self.categories.index(most_probable_category)
        
        return most_probable_category_id

    def find_first_index_less_than_threshold(self, sorted_list, threshold=0.3):
        low, high = 0, len(sorted_list) - 1
        
        while low <= high:
            mid = (low + high) // 2
            if sorted_list[mid] < threshold:
                # If this item is smaller than the threshold, 
                # then check if the previous item is not smaller than the threshold
                # If so, then this is the first occurrence.
                # If not, continue the search in the left half.
                if mid == 0 or sorted_list[mid - 1] >= threshold:
                    return mid
                high = mid - 1
            else:
                # If this item is not smaller than the threshold,
                # then continue the search in the right half.
                low = mid + 1
        
        return 0
    
    def update_candidate_labels(self,most_probable_categories):
        list_of_words_present = list_of_words.copy()
        for cat in most_probable_categories:
            if cat in list_of_words:
                list_of_words_present.remove(cat)
        return list_of_words_present
    
    def get_most_probable_with_bert(self, sentence, most_probable_categories):
        print("==============*************===============")
        print('Using Bert to find most probable category!!')
        print("Incoming sentence: ", sentence)
        if sentence == '':
            return []
        print("Incoming classes: ", list_of_words)
        list_of_words_present = list_of_words.copy()
        if most_probable_categories:
            list_of_words_present = self.update_candidate_labels(most_probable_categories)
        
        result = classifier(sentence, candidate_labels=list_of_words_present, multi_class=True)
        print("===== LABELS AND SCORES =====")
        print(result['labels'][:5])
        print(result['scores'][:5])
        idx = self.find_first_index_less_than_threshold(result['scores'], 0.95)
        if idx == 0:
            idx = self.find_first_index_less_than_threshold(result['scores'], 0.90)
            if idx==0:
                idx=1
        print("==============*************===============")
        return result['labels'][:idx]
    
    def handle_general_conversation(self, most_probable_category, wrong_class, node_stack):
        most_probable_category_id = self.most_probable_id(most_probable_category)
        
        if self.categories[most_probable_category_id] == correction_word:
            most_probable_category = correction_word
            return self.handle_wrong_classification(most_probable_category, wrong_class, node_stack)
        
        audio_path = self.get_audio_path(most_probable_category_id)
        if self.next_nodes:
            try:
                next_node = self.next_nodes[most_probable_category_id]
            except:
                next_node = self.next_nodes[0]
        else:
            next_node = None
        return next_node, audio_path, False, node_stack
    
    def get_current_cat(self, most_probable_categories):
        if correction_word in most_probable_categories:
            return correction_word, [correction_word]
        print('=======> to check from: ',self.categories)
        for category in self.categories:
            print(f'Checking for: {category} in {most_probable_categories}')
            if category in most_probable_categories:
                most_probable_categories.remove(category)
                return category, most_probable_categories
        
        return correction_word, most_probable_categories
    
    def get_next_cat(self, most_probable_categories, check_cats):
        if correction_word in most_probable_categories:
            return correction_word
        for category in check_cats:
            if category in most_probable_categories:
                return category
        return None
    
    def get_response_and_node_info(self, most_probable_category, wrong_class=False, node_stack=None):
        if self.end_node == True:
            return self.handle_end_node(node_stack)
        
        if not self.check_function:
            if most_probable_category == correction_word:
                return self.handle_wrong_classification(most_probable_category, wrong_class, node_stack)
        
        return self.handle_general_conversation(most_probable_category, wrong_class, node_stack)

    def process_text(self, text, wrong_class=False, most_probable_categories=None, node_stack=None):
        print("********************** NEW NODE ************************")
        print(f"Processing text in node: {self.node_name}")
        print(f"Input Text: ", text)
        print(f"Already Found MPC: {most_probable_categories}")
        print(f"Wrong Class: ", wrong_class)
        print(f"Node Categories", self.categories)
        # import pdb; pdb.set_trace()
        self.text = text
        node_stack.append(self)
        new_most_probable_categories = self.get_most_probable_with_bert(text, most_probable_categories)
        
        if most_probable_categories:
            most_probable_categories = most_probable_categories + new_most_probable_categories
        else:
            most_probable_categories = new_most_probable_categories
        most_probable_categories = list(set(most_probable_categories))
        print('New Most Probable categories: ', most_probable_categories)

        # handling misunderstanding at top priority
        if most_probable_categories[0] == correction_word:
            next_node, audio_path, wrong_class, node_stack = self.get_response_and_node_info(correction_word, wrong_class, node_stack)
        currently_use_category, most_probable_categories = self.get_current_cat(most_probable_categories)
        # assuming the last question will surely be answered.
        next_node, audio_path, wrong_class, node_stack = self.get_response_and_node_info(currently_use_category, wrong_class, node_stack)
        if next_node:
            next_cat_check = self.get_next_cat(most_probable_categories, next_node.categories)
            if next_cat_check:
                next_node, audio_path, wrong_class, most_probable_categories, node_stack = next_node.process_text('',wrong_class, most_probable_categories, node_stack)
        return next_node, audio_path, wrong_class, most_probable_categories, node_stack