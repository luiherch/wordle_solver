from load_screen import LoadScreen
from solver import WordleSolver, load_words
from solver_gui import WordleSolverApp
import threading
import queue
import logging

logging.basicConfig(level=logging.INFO)

q = queue.Queue()


def build_app(solver):
    app = WordleSolverApp(solver)
    app.mainloop()


def init_solver():
    word_pool = load_words()
    word_pool = set(list(word_pool)[0:2000])
    wordle_solver = WordleSolver(word_pool)
    wordle_solver.compute_all()
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
