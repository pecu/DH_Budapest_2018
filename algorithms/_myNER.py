import nltk
from nltk import word_tokenize, pos_tag, ne_chunk
sentence = "Mark and John are working at Google."
 
print( ne_chunk(pos_tag(word_tokenize(sentence))) )

from nltk.chunk import conlltags2tree, tree2conlltags
 
sentence = "Mark and John are working at Google."
ne_tree = ne_chunk(pos_tag(word_tokenize(sentence)))
 
iob_tagged = tree2conlltags(ne_tree)
print (iob_tagged)
"""
[('Mark', 'NNP', u'B-PERSON'), ('and', 'CC', u'O'), ('John', 'NNP', u'B-PERSON'), ('are', 'VBP', u'O'), ('working', 'VBG', u'O'), ('at', 'IN', u'O'), ('Google', 'NNP', u'B-ORGANIZATION'), ('.', '.', u'O')]
"""
 
ne_tree = conlltags2tree(iob_tagged)
print (ne_tree)


import os
import collections
 
ner_tags = collections.Counter()
 
corpus_root = "./gmb/gmb-2.2.0"   # Make sure you set the proper path to the unzipped corpus
 
for root, dirs, files in os.walk(corpus_root):
    for filename in files:
        if filename.endswith(".tags"):
            with open(os.path.join(root, filename), 'rb') as file_handle:
                file_content = file_handle.read().decode('utf-8').strip()
                annotated_sentences = file_content.split('\n\n')   # Split sentences
                for annotated_sentence in annotated_sentences:
                    annotated_tokens = [seq for seq in annotated_sentence.split('\n') if seq]  # Split words
 
                    standard_form_tokens = []
 
                    for idx, annotated_token in enumerate(annotated_tokens):
                        annotations = annotated_token.split('\t')   # Split annotations
                        word, tag, ner = annotations[0], annotations[1], annotations[3]
 
                        ner_tags[ner] += 1
 
print (ner_tags)
"""
Counter({u'O': 1146068, u'geo-nam': 58388, u'org-nam': 48034, u'per-nam': 23790, u'gpe-nam': 20680, u'tim-dat': 12786, u'tim-dow': 11404, u'per-tit': 9800, u'per-fam': 8152, u'tim-yoc': 5290, u'tim-moy': 4262, u'per-giv': 2413, u'tim-clo': 891, u'art-nam': 866, u'eve-nam': 602, u'nat-nam': 300, u'tim-nam': 146, u'eve-ord': 107, u'per-ini': 60, u'org-leg': 60, u'per-ord': 38, u'tim-dom': 10, u'per-mid': 1, u'art-add': 1})
"""

ner_tags = collections.Counter()
 
for root, dirs, files in os.walk(corpus_root):
    for filename in files:
        if filename.endswith(".tags"):
            with open(os.path.join(root, filename), 'rb') as file_handle:
                file_content = file_handle.read().decode('utf-8').strip()
                annotated_sentences = file_content.split('\n\n')   # Split sentences
                for annotated_sentence in annotated_sentences:
                    annotated_tokens = [seq for seq in annotated_sentence.split('\n') if seq]  # Split words
 
                    standard_form_tokens = []
 
                    for idx, annotated_token in enumerate(annotated_tokens):
                        annotations = annotated_token.split('\t')   # Split annotation
                        word, tag, ner = annotations[0], annotations[1], annotations[3]
 
                        # Get only the primary category
                        if ner != 'O':
                            ner = ner.split('-')[0]
 
                        ner_tags[ner] += 1
 
print (ner_tags)
# Counter({u'O': 1146068, u'geo': 58388, u'org': 48094, u'per': 44254, u'tim': 34789, u'gpe': 20680, u'art': 867, u'eve': 709, u'nat': 300})
 
print ("Words=", sum(ner_tags.values()))
# Words= 1354149


import string
from nltk.stem.snowball import SnowballStemmer
 
 
def features(tokens, index, history):
    """
    `tokens`  = a POS-tagged sentence [(w1, t1), ...]
    `index`   = the index of the token we want to extract features for
    `history` = the previous predicted IOB tags
    """
 
    # init the stemmer
    stemmer = SnowballStemmer('english')
 
    # Pad the sequence with placeholders
    tokens = [('[START2]', '[START2]'), ('[START1]', '[START1]')] + list(tokens) + [('[END1]', '[END1]'), ('[END2]', '[END2]')]
    history = ['[START2]', '[START1]'] + list(history)
 
    # shift the index with 2, to accommodate the padding
    index += 2
 
    word, pos = tokens[index]
    prevword, prevpos = tokens[index - 1]
    prevprevword, prevprevpos = tokens[index - 2]
    nextword, nextpos = tokens[index + 1]
    nextnextword, nextnextpos = tokens[index + 2]
    previob = history[index - 1]
    contains_dash = '-' in word
    contains_dot = '.' in word
    allascii = all([True for c in word if c in string.ascii_lowercase])
 
    allcaps = word == word.capitalize()
    capitalized = word[0] in string.ascii_uppercase
 
    prevallcaps = prevword == prevword.capitalize()
    prevcapitalized = prevword[0] in string.ascii_uppercase
 
    nextallcaps = prevword == prevword.capitalize()
    nextcapitalized = prevword[0] in string.ascii_uppercase
 
    return {
        'word': word,
        'lemma': stemmer.stem(word),
        'pos': pos,
        'all-ascii': allascii,
 
        'next-word': nextword,
        'next-lemma': stemmer.stem(nextword),
        'next-pos': nextpos,
 
        'next-next-word': nextnextword,
        'nextnextpos': nextnextpos,
 
        'prev-word': prevword,
        'prev-lemma': stemmer.stem(prevword),
        'prev-pos': prevpos,
 
        'prev-prev-word': prevprevword,
        'prev-prev-pos': prevprevpos,
 
        'prev-iob': previob,
 
        'contains-dash': contains_dash,
        'contains-dot': contains_dot,
 
        'all-caps': allcaps,
        'capitalized': capitalized,
 
        'prev-all-caps': prevallcaps,
        'prev-capitalized': prevcapitalized,
 
        'next-all-caps': nextallcaps,
        'next-capitalized': nextcapitalized,
    }
def to_conll_iob(annotated_sentence):
    """
    `annotated_sentence` = list of triplets [(w1, t1, iob1), ...]
    Transform a pseudo-IOB notation: O, PERSON, PERSON, O, O, LOCATION, O
    to proper IOB notation: O, B-PERSON, I-PERSON, O, O, B-LOCATION, O
    """
    proper_iob_tokens = []
    for idx, annotated_token in enumerate(annotated_sentence):
        tag, word, ner = annotated_token
 
        if ner != 'O':
            if idx == 0:
                ner = "B-" + ner
            elif annotated_sentence[idx - 1][2] == ner:
                ner = "I-" + ner
            else:
                ner = "B-" + ner
        proper_iob_tokens.append((tag, word, ner))
    return proper_iob_tokens
 
 
def read_gmb(corpus_root):
    for root, dirs, files in os.walk(corpus_root):
        for filename in files:
            if filename.endswith(".tags"):
                with open(os.path.join(root, filename), 'rb') as file_handle:
                    file_content = file_handle.read().decode('utf-8').strip()
                    annotated_sentences = file_content.split('\n\n')
                    for annotated_sentence in annotated_sentences:
                        annotated_tokens = [seq for seq in annotated_sentence.split('\n') if seq]
 
                        standard_form_tokens = []
 
                        for idx, annotated_token in enumerate(annotated_tokens):
                            annotations = annotated_token.split('\t')
                            word, tag, ner = annotations[0], annotations[1], annotations[3]
 
                            if ner != 'O':
                                ner = ner.split('-')[0]
 
                            if tag in ('LQU', 'RQU'):   # Make it NLTK compatible
                                tag = "``"
 
                            standard_form_tokens.append((word, tag, ner))
 
                        conll_tokens = to_conll_iob(standard_form_tokens)
 
                        # Make it NLTK Classifier compatible - [(w1, t1, iob1), ...] to [((w1, t1), iob1), ...]
                        # Because the classfier expects a tuple as input, first item input, second the class
                        yield [((w, t), iob) for w, t, iob in conll_tokens]
 
reader = read_gmb(corpus_root)


print( reader.__next__())
print( '------------')
"""
[((u'Thousands', u'NNS'), u'O'), ((u'of', u'IN'), u'O'), ((u'demonstrators', u'NNS'), u'O'), ((u'have', u'VBP'), u'O'), ((u'marched', u'VBN'), u'O'), ((u'through', u'IN'), u'O'), ((u'London', u'NNP'), u'B-geo'), ((u'to', u'TO'), u'O'), ((u'protest', u'VB'), u'O'), ((u'the', u'DT'), u'O'), ((u'war', u'NN'), u'O'), ((u'in', u'IN'), u'O'), ((u'Iraq', u'NNP'), u'B-geo'), ((u'and', u'CC'), u'O'), ((u'demand', u'VB'), u'O'), ((u'the', u'DT'), u'O'), ((u'withdrawal', u'NN'), u'O'), ((u'of', u'IN'), u'O'), ((u'British', u'JJ'), u'B-gpe'), ((u'troops', u'NNS'), u'O'), ((u'from', u'IN'), u'O'), ((u'that', u'DT'), u'O'), ((u'country', u'NN'), u'O'), ((u'.', u'.'), u'O')]
------------
"""
 
print( reader.__next__())
print( '------------')
"""
[((u'Families', u'NNS'), u'O'), ((u'of', u'IN'), u'O'), ((u'soldiers', u'NNS'), u'O'), ((u'killed', u'VBN'), u'O'), ((u'in', u'IN'), u'O'), ((u'the', u'DT'), u'O'), ((u'conflict', u'NN'), u'O'), ((u'joined', u'VBD'), u'O'), ((u'the', u'DT'), u'O'), ((u'protesters', u'NNS'), u'O'), ((u'who', u'WP'), u'O'), ((u'carried', u'VBD'), u'O'), ((u'banners', u'NNS'), u'O'), ((u'with', u'IN'), u'O'), ((u'such', u'JJ'), u'O'), ((u'slogans', u'NNS'), u'O'), ((u'as', u'IN'), u'O'), ((u'"', '``'), u'O'), ((u'Bush', u'NNP'), u'B-per'), ((u'Number', u'NN'), u'O'), ((u'One', u'CD'), u'O'), ((u'Terrorist', u'NN'), u'O'), ((u'"', '``'), u'O'), ((u'and', u'CC'), u'O'), ((u'"', '``'), u'O'), ((u'Stop', u'VB'), u'O'), ((u'the', u'DT'), u'O'), ((u'Bombings', u'NNS'), u'O'), ((u'.', u'.'), u'O'), ((u'"', '``'), u'O')]
------------
"""
 
print( reader.__next__())
print( '------------')
"""
[((u'They', u'PRP'), u'O'), ((u'marched', u'VBD'), u'O'), ((u'from', u'IN'), u'O'), ((u'the', u'DT'), u'O'), ((u'Houses', u'NNS'), u'O'), ((u'of', u'IN'), u'O'), ((u'Parliament', u'NN'), u'O'), ((u'to', u'TO'), u'O'), ((u'a', u'DT'), u'O'), ((u'rally', u'NN'), u'O'), ((u'in', u'IN'), u'O'), ((u'Hyde', u'NNP'), u'B-geo'), ((u'Park', u'NNP'), u'I-geo'), ((u'.', u'.'), u'O')]
------------
"""

import pickle
from collections import Iterable
from nltk.tag import ClassifierBasedTagger
from nltk.chunk import ChunkParserI
 
 
class NamedEntityChunker(ChunkParserI):
    def __init__(self, train_sents, **kwargs):
        assert isinstance(train_sents, Iterable)
 
        self.feature_detector = features
        self.tagger = ClassifierBasedTagger(
            train=train_sents,
            feature_detector=features,
            **kwargs)
 
    def parse(self, tagged_sent):
        chunks = self.tagger.tag(tagged_sent)
 
        # Transform the result from [((w1, t1), iob1), ...] 
        # to the preferred list of triplets format [(w1, t1, iob1), ...]
        iob_triplets = [(w, t, c) for ((w, t), c) in chunks]
 
        # Transform the list of triplets to nltk.Tree format
        return conlltags2tree(iob_triplets)
 
 
    
reader = read_gmb(corpus_root)
data = list(reader)
training_samples = data[:int(len(data) * 0.9)]
test_samples = data[int(len(data) * 0.9):]
 
print( "#training samples = %s" % len(training_samples))    # training samples = 55809
print( "#test samples = %s" % len(test_samples))

chunker = NamedEntityChunker(training_samples[:2000])

from nltk import pos_tag, word_tokenize

file = open('./input.txt','r')
fout = open('./NER.txt','w')
fout.write( str(chunker.parse(pos_tag(word_tokenize(file.read())))))
score = chunker.evaluate([conlltags2tree([(w, t, iob) for (w, t), iob in iobs]) for iobs in test_samples[:500]])
print( score.accuracy() )        # 0.931132334092 - Awesome :D
file.close()
fout.close()
    


    