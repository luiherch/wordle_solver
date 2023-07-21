import customtkinter as ctk
import numpy as np
from functools import partial
import logging
import copy
import itertools
from PIL import Image
from solver import WordleSolver
import keyboard
import threading


class WordleSolverApp(ctk.CTk):
    def __init__(self, solver):
        super().__init__()

        self.width = 800
        self.height = 750
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x_coord = int((screen_width / 2) - (self.width / 2))
        y_coord = int((screen_height / 2) - (self.height / 2))

        self.app_title = "Wordle Solver"
        self.geometry(f"{self.width}x{self.height}+{x_coord}+{y_coord}")
        self.color_mode = "dark"
        ctk.set_appearance_mode(self.color_mode)
        self.settings_window = None
        self.wm_iconbitmap("img/logo_light.ico")
        self.winfo_toplevel().title("Wordle Solver")

        self.title_font = ctk.CTkFont(family="Roboto", size=22, weight="bold")
        self.main_font = ctk.CTkFont(family="Roboto", size=16, weight="bold")
        self.sub_header_font = ctk.CTkFont(family="Robot", size=18, weight="bold")

        self.settings_image = ctk.CTkImage(
            dark_image=Image.open("img/settings_light.png"),
            light_image=Image.open("img/settings_dark.png"),
            size=(24, 24),
        )
        self.reset_image = ctk.CTkImage(
            dark_image=Image.open("img/reset_light.png"),
            light_image=Image.open("img/reset_dark.png"),
            size=(24, 24),
        )

        self.pointer = (0, 0)
        self.color_matrix = np.zeros([6, 5], dtype=int)
        self.letter_matrix = np.empty([6, 5], dtype=str)
        self.game_grid = {}

        self.solver = solver
        self.main_pool = copy.deepcopy(self.solver.word_pool)
        self.main_h_dict = copy.deepcopy(self.solver.h_dict)

        self.vkeyboard_option = ctk.StringVar(value="Default")
        self.vkeyboard_buttons = {}

        self.nav = ctk.CTkFrame(self, width=450, height=30)
        self.game_container = ctk.CTkFrame(self, width=50)
        self.footer = ctk.CTkFrame(self, width=450, height=30)

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.nav.grid(row=0)
        self.game_container.grid(row=1, sticky="nsew")
        self.footer.grid(row=4, sticky="ew")

        self.title_label = ctk.CTkLabel(
            self.nav, text=self.app_title, font=self.title_font
        )
        self.compute_button = ctk.CTkButton(
            self.nav,
            text="Compute entropies",
            command=self.compute_entropies,
            font=self.main_font,
        )
        self.show_button = ctk.CTkButton(
            self.nav,
            text="Show entropies",
            command=self.show_entropies,
            font=self.main_font,
        )
        self.title_label.grid(row=0, columnspan=3)
        self.compute_button.grid(row=1, column=1, padx=4)
        self.show_button.grid(row=1, column=2, padx=4)

        self.game_container.grid_rowconfigure(0, weight=1)
        self.game_container.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        self.game_mid = ctk.CTkFrame(
            self.game_container, width=250, height=200, fg_color=("#e4e5f1", "gray20")
        )
        self.game_mid.grid(row=0, column=2, sticky="nsew")

        # create the center containers
        self.game_mid.grid_rowconfigure((1, 2), weight=1)
        self.game_mid.grid_columnconfigure((0, 1), weight=1)

        self.settings_frame = ctk.CTkFrame(
            self.game_mid, width=50, height=40, fg_color="transparent"
        )
        self.screen_container = ctk.CTkFrame(
            self.game_mid, width=250, height=190, fg_color="transparent"
        )
        self.vkeyboard_container = ctk.CTkFrame(
            self.game_mid, width=100, height=190, fg_color="transparent"
        )

        self.settings_frame.grid(row=0, column=1)
        self.screen_container.grid(row=1, column=0, pady=4)
        self.vkeyboard_container.grid(row=2, column=0, pady=8)

        self.reset_button = ctk.CTkButton(
            self.settings_frame,
            width=30,
            height=30,
            image=self.reset_image,
            text="",
            fg_color="transparent",
            command=self.reset,
        )
        self.settings_button_v2 = ctk.CTkButton(
            self.settings_frame,
            width=30,
            height=30,
            image=self.settings_image,
            text="",
            fg_color="transparent",
            command=self.open_settings,
        )
        self.reset_button.grid(row=0, column=0)
        self.settings_button_v2.grid(row=0, column=1)

        self.build_screen_buttons()

        self.label_container = ctk.CTkFrame(
            self.game_mid, width=100, height=190, fg_color="transparent"
        )
        self.label_container.grid(row=1, column=1)
        self.entropies_container = ctk.CTkFrame(
            self.label_container, width=95, height=100
        )
        self.entropies_container.grid(row=1, column=1)

        self.guesses_label = ctk.CTkLabel(
            self.entropies_container,
            text="Top words",
            width=100,
            height=30,
            padx=6,
            pady=4,
            font=self.main_font,
        )
        self.guesses_label.grid(row=0, column=0)
        self.entropy_labels = {}
        self.populate_entropy_labels()
        self.virtual_keyboard()
        self.delete = ctk.CTkButton(
            self.vkeyboard_container,
            text="DEL",
            height=46,
            width=46,
            command=self.erase_letter,
            font=self.main_font,
        ).grid(row=0, column=9, padx=3)

        self.bind("<FocusIn>", self.start_reading_thread)
        self.bind("<FocusOut>", self.stop_reading_thread)
        self.reading_thread = None

    def open_settings(self):
        if self.settings_window is None or not self.settings_window.winfo_exists():
            self.settings_window = Settings(self)
        else:
            self.settings_window.focus()

    def build_screen_buttons(self):
        for i in range(6):
            for j in range(5):
                self.game_grid[(i, j)] = ctk.CTkButton(
                    self.screen_container,
                    text="",
                    width=46,
                    height=46,
                    command=partial(self.click_color_button, (i, j)),
                    fg_color="#cac7c2",
                    font=self.main_font,
                )
                self.game_grid[(i, j)].grid(row=i, column=j, padx=3, pady=5)

    def populate_entropy_labels(self):
        top_entropies = self.solver.show_entropies()
        for l in range(10):
            self.entropy_labels[l] = ctk.CTkLabel(
                self.entropies_container,
                text=top_entropies[l],
                width=70,
                height=30,
                padx=8,
                pady=4,
                font=self.main_font,
            )
            self.entropy_labels[l].grid(row=l + 1, column=0)

    def virtual_keyboard(self, option="Default"):
        if option == "Default":
            self.keyboard = [chr(x) for x in range(65, 91)]
            self.keyboard.insert(14, "Ñ")
        elif option == "QWERTY":
            self.keyboard = "QWERTYUIOPASDFGHJKLÑZXCVBNM"
            self.keyboard = [l for l in self.keyboard]
        j = 0
        for ind, button in enumerate(self.keyboard):
            if ind % 9 == 0 and ind != 0:
                j = j + 1
            self.vkeyboard_buttons[button] = ctk.CTkButton(
                self.vkeyboard_container,
                text=button,
                width=46,
                height=46,
                command=partial(self.click_vletter, button),
                font=self.main_font,
            )
            self.vkeyboard_buttons[button].grid(row=j, column=ind % 9, padx=3, pady=5)

    def click_color_button(self, pos):
        color = self.game_grid[pos].cget("fg_color")
        if color == "#cac7c2":
            color = "#97db46"
            self.color_matrix[pos] = 2
        elif color == "#97db46":
            color = "#e8d32b"
            self.color_matrix[pos] = 1
        elif color == "#e8d32b":
            color = "#cac7c2"
            self.color_matrix[pos] = 0
        self.game_grid[pos].configure(fg_color=color)

    def click_vletter(self, s):
        print(self.pointer)
        self.game_grid[self.pointer].configure(text=s, text_color="black")
        self.letter_matrix[self.pointer] = s
        i, j = self.pointer
        if j == 4:
            i = i + 1
        self.pointer = (i, (j + 1) % 5)

    def erase_letter(self):
        i, j = self.pointer
        if self.pointer == (0, 0):
            return
        else:
            if j == 0:
                j = 4
                i = i - 1
            else:
                j = j - 1
        self.pointer = (i, j)
        self.game_grid[self.pointer].configure(text="")
        self.letter_matrix[self.pointer] = ""

    def compute_entropies(self):
        i, _ = self.pointer
        to_reduce = {
            "".join(self.letter_matrix[x]): tuple(self.color_matrix[x])
            for x in range(i)
        }
        if not to_reduce:
            logging.debug(f"No words to reduce")
            MessageScreen(
                text=f"Please, add a word to reduce the word pool", title="Warning"
            )
            return
        logging.info("Reducing word_pool...")
        to_check = [k.lower() for k in to_reduce.keys()]
        missing_words = self.solver.check_existence(to_check)
        if not missing_words:
            # self.solver.reduce_pool(to_reduce)
            self.solver.cross_pool(to_reduce)
            self.solver.compute_entropies(first_time=False)
            self.solver.par = itertools.product(self.solver.word_pool, repeat=2)
            logging.info("Reduced")
        else:
            logging.debug(f"These words are not in the word pool: {missing_words}")
            MessageScreen(
                text=f"The following words do not exist: {missing_words}",
                title="Warning",
            )

    def show_entropies(self):
        top_picks = self.solver.show_entropies()
        for ind, pick in enumerate(top_picks):
            self.entropy_labels[ind].configure(text=pick)

    def toggle_appearance_mode(self):
        if self.color_mode == "dark":
            self.color_mode = "light"
        else:
            self.color_mode = "dark"

        ctk.set_appearance_mode(self.color_mode)

    def reset(self):
        self.solver = WordleSolver.from_cache(
            word_pool=self.main_pool, h_dict=self.main_h_dict
        )
        self.solver.compute_entropies()

    def read_keyboard_input(self):
        while self.reading_thread and self.focus_get() == self:
            event = keyboard.read_event(suppress=False)
            if event.event_type == keyboard.KEY_UP:
                char = event.name
                if char == "backspace":
                    self.erase_letter()
                elif char.isalpha() and len(char) == 1:
                    self.click_vletter(char.upper())
                else:
                    logging.debug("Not alpha")

    def start_reading_thread(self, event):
        if not self.reading_thread:
            self.reading_thread = threading.Thread(target=self.read_keyboard_input)
            self.reading_thread.daemon = True
            self.reading_thread.start()

    def stop_reading_thread(self, event):
        self.reading_thread.stop()
        self.reading_thread = None


class Settings(ctk.CTkToplevel):
    def __init__(self, *args, **kwargs):
        self.dad = args[0]
        super().__init__(*args, **kwargs)

        self.width = 400
        self.height = 250
        self.geometry(f"{self.width}x{self.height}+{self.width}+{self.height}")
        self.grid_rowconfigure((0, 1, 2), weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.vkeyboard_values = ["Default", "QWERTY"]
        self.winfo_toplevel().title("Wordle Solver Settings")

        self.sub_header_font = ctk.CTkFont(family="Robot", size=18, weight="bold")

        self.label = ctk.CTkLabel(
            self, text="Settings", font=self.sub_header_font
        ).grid(row=0, column=0)
        self.appearance_mode = ctk.CTkSwitch(
            self,
            text="Light Mode",
            onvalue="Dark",
            offvalue="Light",
            command=self.dad.toggle_appearance_mode,
        ).grid(row=1, column=0)
        self.vkeyboard_mode = ctk.CTkOptionMenu(
            self,
            values=self.vkeyboard_values,
            command=self.dad.virtual_keyboard,
            variable=self.dad.vkeyboard_option,
        ).grid(row=2, column=0)

        self.after(150, lambda: self.focus())


class MessageScreen(ctk.CTkInputDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _create_widgets(self):
        self.grid_columnconfigure((0, 1), weight=1)
        self.rowconfigure(0, weight=1)

        self._label = ctk.CTkLabel(
            master=self,
            width=300,
            wraplength=300,
            fg_color="transparent",
            text_color=self._text_color,
            text=self._text,
        )
        self._label.grid(row=0, column=0, columnspan=2, padx=20, pady=20, sticky="ew")

        self._ok_button = ctk.CTkButton(
            master=self,
            width=100,
            border_width=0,
            fg_color=self._button_fg_color,
            hover_color=self._button_hover_color,
            text_color=self._button_text_color,
            text="Accept",
            command=self._ok_event,
        )
        self._ok_button.grid(
            row=2, column=0, columnspan=2, padx=(20, 10), pady=(0, 20), sticky="ew"
        )

        self.after(150, lambda: self.focus())

    def _ok_event(self, event=None):
        self.grab_release()
        self.destroy()
