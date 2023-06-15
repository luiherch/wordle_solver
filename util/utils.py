import re
import json
from unicodedata import normalize
import time
import logging
from functools import wraps
import pathlib


def create_word_pool():
    with open("data/0_palabras_todas_no_conjugaciones.txt", "r", encoding="utf-8") as f:
        all_words = f.readlines()
    all_words = [word[:-1] for word in all_words]
    five_letters = [word for word in all_words if len(word) == 5]
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


def coroutine(func):
    def start(*args, **kwargs):
        cr = func(*args, **kwargs)
        next(cr)
        return cr

    return start


def timeit(func):
    @wraps(func)
    def timeit_wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        total_time = end_time - start_time
        logging.debug(
            f"Function {func.__name__}{args} {kwargs} Took {total_time:.4f} seconds"
        )
        return result

    return timeit_wrapper


def load_words(path):
    with open(path, "r") as f:
        word_pool = json.load(f)
    return set(word_pool)


def load_cache(path):
    with open(path, "r") as f:
        h_dict = json.load(f)
    return h_dict


def convert_tuples_to_strings(dict_:dict):
        converted_dict = {}
        for key, value in dict_.items():
            if isinstance(key, tuple):
                key = str(key)
            if isinstance(value, dict):
                value = convert_tuples_to_strings(value)
            converted_dict[key] = value
        return converted_dict
