import itertools
from scipy import stats
from heapq import nlargest
import json
from util.utils import timeit, coroutine


class WordleSolver:
    def __init__(self, word_pool) -> None:
        self.w_dict = {}
        self.h_dict = {}
        self.word_pool = word_pool
        self.par = itertools.product(self.word_pool, repeat=2)
        self.patterns = tuple(itertools.product((0, 1, 2), repeat=5))

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

    def init_all(self):
        for word in self.word_pool:
            self.w_dict[word] = {x: [] for x in self.patterns}

    @timeit
    def compute_word_dict(self):
        self.init_all()
        cor = self.compute_entropies_cor()
        previous = None
        for w1, w2 in self.par:
            if w1 != previous and previous is not None:
                cor.send(previous)
            pattern = self.word_pattern(w1, w2)
            self.w_dict[w1][pattern].append(w2)
            previous = w1
        cor.close()

    @coroutine
    def compute_entropies_cor(self):
        while True:
            word = yield
            pk = [len(self.w_dict[word][comb]) for comb in self.patterns]
            self.h_dict[word] = stats.entropy(pk, base=2)

    def reduce_pool(self, to_reduce):
        sets = {k.lower(): set(self.w_dict[k.lower()][v]) for k, v in to_reduce.items()}
        reduced_pool = set.intersection(*sets.values())
        self.word_pool = reduced_pool
        self.par = itertools.product(self.word_pool, repeat=2)

    def compute_all(self):
        self.w_dict = {}
        self.h_dict = {}
        self.compute_word_dict()

    @coroutine
    def compute_word_dict_cor(self):
        self.init_all()
        cor = self.compute_entropies_cor()
        previous = None
        for w1, w2 in self.par:
            if w1 != previous and previous is not None:
                cor.send(previous)
                yield
            pattern = self.word_pattern(w1, w2)
            self.w_dict[w1][pattern].append(w2)
            previous = w1
        cor.close()

    def check_existence(self, items):
        items = set(items)
        exist_dict = {elem: elem in self.word_pool for elem in items}
        not_exists = [k for k, v in exist_dict.items() if v is False]
        return not_exists

    def show_entropies(self):
        print(nlargest(5, self.h_dict, key=self.h_dict.get))
        return list(nlargest(10, self.h_dict, key=self.h_dict.get))


def load_words():
    with open("data/palabras.json", "r") as openfile:
        word_pool = json.load(openfile)
    return set(word_pool)
