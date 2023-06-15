from load_screen import LoadScreen
from solver import WordleSolver
from solver_gui import WordleSolverApp
import threading
import queue
import logging
import pathlib
from util.utils import load_cache, load_words

logging.basicConfig(level=logging.INFO)

q = queue.Queue()
script_dir = pathlib.Path(__file__).resolve().parent
data_file = script_dir / "data" / "palabras.json"
cache_file = script_dir / "cache" / "h_dict.json"


def build_app(solver):
    app = WordleSolverApp(solver)
    app.mainloop()


def init_solver():
    word_pool = load_words(data_file)

    if cache_file.is_file():
        cache = load_cache(cache_file)
        wordle_solver = WordleSolver.from_cache(word_pool, cache)
        wordle_solver.compute_entropies()
    else:
        wordle_solver = WordleSolver(word_pool)
        wordle_solver.compute_entropies()
        wordle_solver.entropies_to_json()

    q.put(wordle_solver)


def after_callback():
    try:
        item = q.get(block=False)
    except queue.Empty:
        app.after(100, after_callback)
        app.update_idletasks()
        return

    if item is not None:
        app.progressbar.stop()
        logging.info("Solver succesfully initialised")
        app.destroy()
        build_app(item)


app = LoadScreen()
threading.Thread(target=init_solver).start()
app.after(500, after_callback)
app.mainloop()
