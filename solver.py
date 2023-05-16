import re
from unicodedata import normalize
from itertools import product
from scipy import stats
from heapq import nlargest
import stanza
import json


def lemmatizer(pool: list):
    processor_dict = {
        "tokenize": "gsd",
        "pos": "hdt",
        "ner": "conll03",
        "lemma": "default",
    }
    stanza.download("es", processors=processor_dict, package=None)
    nlp = stanza.Pipeline(
        "es", processors=processor_dict, package=None, download_method=None
    )
    lemmas = []
    lemmas = [nlp(word).sentences[0].words[0].lemma for word in pool]
    post_lemma = [word for word in lemmas if len(word) == 5]
    return post_lemma


class WordleSolver:
    def __init__(self, word_pool) -> None:
        self.w_dict = {}
        self.h_dict = {}
        self.word_pool = word_pool
        self.par = product(self.word_pool, repeat=2)
        self.patterns = tuple(product((0, 1, 2), repeat=5))
        self.compute_all()

    @staticmethod
    def word_pattern(w1, w2):
        index = (0, 1, 2, 3, 4)
        pattern = [0, 0, 0, 0, 0]
        for ind, a, b in zip(index, w1, w2):
            if a == b:
                pattern[ind] = 2
            elif a in w2:
                pattern[ind] = 1
        return tuple(pattern)

    def compute_word_dict(self):
        for word in self.word_pool:
            self.w_dict[word] = {x: [] for x in self.patterns}
        for words in self.par:
            w1, w2 = words
            pattern = word_pattern(w1, w2)
            self.w_dict[w1][pattern].append(w2)

    def compute_entropies(self):
        for word in self.w_dict:
            pk = []
            for comb in self.patterns:
                pk.append(len(self.w_dict[word][comb]))
            self.h_dict[word] = stats.entropy(pk, base=2)

    def reduce_pool(self, to_reduce):
        sets = [set(self.w_dict[k.lower()][v]) for k, v in to_reduce.items()]
        reduced_pool = set.intersection(*sets)
        self.word_pool = reduced_pool
        self.par = tuple(product(self.word_pool, repeat=2))

    def compute_all(self):
        self.w_dict = {}
        self.h_dict = {}
        self.compute_word_dict()
        self.compute_entropies()

    def check_existence(self, items):
        exists = [elem in self.word_pool for elem in items]
        return all(exists)

    def show_entropies(self):
        print(nlargest(5, self.h_dict, key=self.h_dict.get))
        return list(nlargest(10, self.h_dict, key=self.h_dict.get))


def create_word_pool(lemma: bool = False):
    with open("data/0_palabras_todas_no_conjugaciones.txt", "r", encoding="utf-8") as f:
        all_words = f.readlines()
    all_words = [word[:-1] for word in all_words]
    five_letters = [word for word in all_words if len(word) == 5]
    if lemma:
        five_letters = lemmatizer(five_letters)
    five_letters_clean = []
    for word in five_letters:
        word = re.sub(
            r"([^n\u0300-\u036f]|n(?!\u0303(?![\u0300-\u036f])))[\u0300-\u036f]+",
            r"\1",
            normalize("NFD", word),
            0,
            re.I,
        )
        five_letters_clean.append(word)
    five_letters_clean = [normalize("NFC", word) for word in five_letters_clean]
    # Eliminar duplicados
    five_letters_clean = set(five_letters_clean)
    word_pool = five_letters_clean
    with open("palabras.json", "w") as outfile:
        ser = json.dumps(list(word_pool))
        outfile.write(ser)
    return word_pool


def load_words():
    with open("data/palabras.json", "r") as openfile:
        word_pool = json.load(openfile)
    return set(word_pool)


def word_pattern(w1, w2):
    index = (0, 1, 2, 3, 4)
    pattern = [0, 0, 0, 0, 0]
    for ind, a, b in zip(index, w1, w2):
        if a == b:
            pattern[ind] = 2
        elif a in w2:
            pattern[ind] = 1
    return tuple(pattern)


def populate_pattern(words: tuple, w_dict: dict):
    w1, w2 = words
    pattern = word_pattern(w1, w2)
    w_dict[w1][pattern].append(w2)


def populate_pattern_multi(words: tuple):
    w1, w2 = words
    p = word_pattern(w1, w2)
    d = {p: w2}
    return {w1: d}


def gen_init_dict(word_pool, patterns):
    w_dict = {}
    for word in word_pool:
        w_dict[word] = {x: [] for x in patterns}
    return w_dict


def populate_entropies(word, patterns, w_dict, h_dict):
    pk = []
    for comb in patterns:
        pk.append(len(w_dict[word][comb]))
    h_dict[word] = stats.entropy(pk, base=2)


def reducer(w_dict: dict, to_reduce: dict) -> set:
    sets = [set(w_dict[k][v]) for k, v in to_reduce.items()]
    reduced_pool = set.intersection(*sets)
    return reduced_pool


def gen_entropies(par, patterns, w_dict):
    h_dict = {}
    for words in par:
        populate_pattern(words, w_dict)
    for word in w_dict:
        populate_entropies(word, patterns, w_dict, h_dict)
    return h_dict
