import spacy
import nltk
from nltk.corpus import wordnet as wn


class Preprocessor:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        nltk.download('wordnet')

    def is_token_word(self, token):
        return not token.is_stop and token.pos_ in ("NOUN", "VERB", "ADJ", "PROPN", "NUM")

    def preprocess(self, text):
        text = text.lower()
        text = self.nlp(text)
        text = list(filter(self.is_token_word, text))
        text = [token.lemma_ for token in text]
        return text




