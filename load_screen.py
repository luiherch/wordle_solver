import tkinter as tk
from tkinter import ttk


class LoadScreen(tk.Tk):
    def __init__(self):
        super().__init__()
        self.width = 400
        self.height = 250
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x_coord = int((screen_width / 2) - (self.width / 2))
        y_coord = int((screen_height / 2) - (self.height / 2))
        self.geometry(f"{self.width}x{self.height}+{x_coord}+{y_coord}")
        self.overrideredirect(1)

        self.title_font = ("Lato", 24, "bold")
        self.loading_font = ("Calibri", 10, "normal")

        self.container = tk.Frame(
            self, width=self.width, height=self.height, bg="#272727"
        ).place(x=0, y=0)
        self.title_label = tk.Label(
            self, text="Wordle Solver", fg="white", bg="#272727"
        )
        self.title_label.configure(font=self.title_font)
        self.title_label.place(x=80, y=90)

        self.progressbar = ttk.Progressbar(mode="indeterminate")
        self.progressbar.place(x=90, y=135, width=202)
        self.progressbar.start(40)

        self.loading_label = tk.Label(self, text="Loading...", fg="white", bg="#272727")
        self.loading_label.configure(font=self.loading_font)
        self.loading_label.place(x=10, y=self.height - 28)

        self.update_idletasks()
