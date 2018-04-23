import nltk
import random
import pickle
from collections import defaultdict
nltk.download('punkt')

with open('entropy_classifier2.pickle', 'rb') as classiefier_file, open('t2.pkl', 'rb') as tagger_file:
    classifier = pickle.load(classiefier_file)
    tagger = pickle.load(tagger_file)


class Chatbot(object):
    def __init__(self):
        self.uncertainty_threshhold = 0.25
        self.classifier = classifier
        self.tagger = tagger

    @staticmethod
    def chat_features(token_message):
        features = {}
        for word in token_message:
            features['contains({})'.format(word.lower())] = True
        return features

    @staticmethod
    def grammar_chunking(sentence):
        grammar = r"""
        LO: {<DT|JJ>*<NNP.*>+}
        PP: {<IN><DT|PRP\$>?<LO>}     # Chunk preposition, determiner/possessive and location
        NP: {<DT|JJ|NN.*>+}           # Chunk sequences of DT, JJ, NN
        VP: {<VB.*><PP>*<NP|LO>}      # Chunk verbs and their arguments
        """
        cp = nltk.RegexpParser(grammar, loop=2)
        return cp.parse(sentence)

    def classify(self, token_message):
        # Generate Chat Features
        features = self.chat_features(token_message)

        # Classify Chat
        dist = self.classifier.prob_classify(features)

        if dist.prob(dist.max()) >= self.uncertainty_threshhold:
            intent = dist.max()
        else:
            intent = None
        return intent

    def extract_key_words(self, query, sentence):
        # Tag the sentence
        tag_sentence = self.tagger.tag(sentence)

        # Chunk the sentence
        chunk_sentence = self.grammar_chunking(tag_sentence)

        # Get the Key words based on Chunk label
        for subtree in chunk_sentence:
            if isinstance(subtree, nltk.tree.Tree) and subtree.label() == 'VP':
                if query['client'] == 'description':
                    query['product'] += " ".join(x[0] for x in subtree[-1] if x[1][:2] == 'NN')
                    query['description'] += " ".join(x[0] for x in subtree[-1] if x[1][:2] == 'JJ')
                else:
                    query['product'] = " ".join([x[0] for x in subtree[-1]])
            elif isinstance(subtree, nltk.tree.Tree) and subtree.label() == 'PP':
                query['location'] += " ".join([x[0] for x in subtree[1]])

        return query

    def process_message(self, message):
        query = defaultdict(str)

        # Tokenize
        token_message = nltk.tokenize.word_tokenize(message)

        # Classify Intent
        query['client'] = self.classify(token_message)

        # Extract key words
        query = self.extract_key_words(query, token_message)

        return query


if __name__ == '__main__':
    chatbot = Chatbot()
    string = input('Ask me anything:')
    query = chatbot.process_message(string)
    for key in query:
        print(key, query[key])
