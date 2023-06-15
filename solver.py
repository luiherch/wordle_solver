import itertools
from scipy import stats
from heapq import nlargest
import json
from util.utils import timeit, coroutine
import pathlib


class WordleSolver:
    def __init__(self, word_pool: set) -> None:
        self.w_dict = {}
        self.h_dict = {}
        self.cache = False
        self.word_pool = word_pool
        self.par = itertools.product(self.word_pool, repeat=2)
        self.patterns = tuple(itertools.product((0, 1, 2), repeat=5))

    @classmethod
    def from_cache(cls, word_pool: set, h_dict: dict):
        if not isinstance(h_dict, dict):
            raise TypeError("h_dict must be a dictionary")
        inst = cls(word_pool)
        inst.h_dict = h_dict
        inst._init_w_dict()
        inst.cache = True
        return inst

    @staticmethod
    def word_pattern(w1: str, w2: str):
        index = (0, 1, 2, 3, 4)
        pattern = [0, 0, 0, 0, 0]
        for ind, a, b in zip(index, w1, w2):
            if a == b:
                pattern[ind] = 2
            elif a in w2:
                pattern[ind] = 1
        return tuple(pattern)

    def _init_w_dict(self):
        for word in self.word_pool:
            self.w_dict[word] = {x: [] for x in self.patterns}

    @coroutine
    def _compute_entropies_cor(self):
        while True:
            word = yield
            pk = [len(self.w_dict[word][comb]) for comb in self.patterns]
            self.h_dict[word] = stats.entropy(pk, base=2)

    @timeit
    def _compute_word_dict(self):
        self._init_w_dict()
        cor = self._compute_entropies_cor()
        previous = None
        for w1, w2 in self.par:
            if w1 != previous and previous is not None:
                cor.send(previous)
            pattern = self.word_pattern(w1, w2)
            self.w_dict[w1][pattern].append(w2)
            previous = w1
        cor.close()

    def compute_entropies(self, first_time: bool = True):
        if first_time and self.cache:
            # If its the first time and you have the cache, return
            return
        self.w_dict = {}
        self.h_dict = {}
        self._compute_word_dict()

    def check_existence(self, items):
        items = set(items)
        exist_dict = {elem: elem in self.word_pool for elem in items}
        not_exists = [k for k, v in exist_dict.items() if v is False]
        return not_exists

    def reduce_pool(self, to_reduce):
        sets = {k.lower(): set(self.w_dict[k.lower()][v]) for k, v in to_reduce.items()}
        reduced_pool = set.intersection(*sets.values())
        self.word_pool = reduced_pool
        self.par = itertools.product(self.word_pool, repeat=2)

    def cross_pool(self, to_reduce):
        pools = []
        for w1, reduce_pattern in to_reduce.items():
            for w2 in self.word_pool:
                pattern = self.word_pattern(w1.lower(), w2)
                self.w_dict[w1.lower()][pattern].append(w2)
            pools.append(set(self.w_dict[w1.lower()][reduce_pattern]))
        new_pool = self.word_pool.intersection(*pools)
        self.word_pool = new_pool
        self.par = itertools.product(self.word_pool, repeat=2)

    def show_entropies(self):
        return list(nlargest(10, self.h_dict, key=self.h_dict.get))

    def entropies_to_json(self):
        script_dir = pathlib.Path(__file__).resolve().parent
        cache_dir = script_dir / "cache"
        cache_dir.mkdir(parents=True, exist_ok=True)
        with open(cache_dir / "h_dict.json", "w") as f:
            json.dump(self.h_dict, f)
