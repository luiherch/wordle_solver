from load_screen import LoadScreen
from solver import WordleSolver
from solver_gui import WordleSolverApp
import threading
import queue
import logging
import os
from util.utils import load_cache, load_words

logging.basicConfig(level=logging.INFO)

q = queue.Queue()


def build_app(solver):
    app = WordleSolverApp(solver)
    app.mainloop()


def init_solver():
    word_pool = load_words()

    if os.path.isfile("cache/h_dict.json"):
        cache = load_cache()
        wordle_solver = WordleSolver.from_cache(word_pool,cache)
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
