import customtkinter as ctk
from solver import WordleSolver, load_words
import numpy as np
from functools import partial
from PIL import Image

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.app_title = "Wordle Solver"
        self.geometry = ('760x480')
        self.font_family = "Roboto"
        self.font_size = 14
        self.font_color = 'white'
        self.color_mode = 'dark'
        ctk.set_appearance_mode(self.color_mode)
        self.settings_window = None
        self.wm_iconbitmap('img/data.ico')
        self.winfo_toplevel().title("Wordle Solver")

        self.title_font = ctk.CTkFont(family="Roboto", size=20, weight="bold")
        self.main_font = ctk.CTkFont(family="Roboto", size=14, weight="normal")

        self.settings_image = ctk.CTkImage(light_image=Image.open('img/settings.png'),size=(30,30))

        self.pointer = (0,0)
        self.color_matrix = np.zeros([6,5], dtype=int)
        self.letter_matrix = np.empty([6,5], dtype=str)
        self.game_grid = {}

        
        word_pool = load_words()
        #word_pool = set(list(word_pool)[0:2000])
        self.solver = WordleSolver(word_pool)

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

        self.settings_button = ctk.CTkButton(self.footer, image=self.settings_image, text="", fg_color="transparent", command=self.open_settings).pack()

        self.title_label = ctk.CTkLabel(self.nav, text=self.app_title, font=self.title_font)
        self.compute_button = ctk.CTkButton(self.nav, text="Compute entropies", command=self.compute_entropies, font=self.main_font)
        self.show_button = ctk.CTkButton(self.nav, text="Show entropies", command=self.show_entropies, font=self.main_font)
        self.title_label.grid(row=0, columnspan=3)
        self.compute_button.grid(row=1, column=2, padx=4)
        self.show_button.grid(row=1, column=1, padx=4)

        self.game_container.grid_rowconfigure(0, weight=1)
        self.game_container.grid_columnconfigure(4, weight=1)

        self.game_left = ctk.CTkFrame(self.game_container, width=50, height=200)
        self.game_mid = ctk.CTkFrame(self.game_container, width=250, height=200)
        self.game_labels = ctk.CTkFrame(self.game_container, width=100, height=200)
        self.game_right = ctk.CTkFrame(self.game_container, width=50, height=200)
        self.game_left.grid(row=0, column=0, sticky="nsew", columnspan=2)
        self.game_mid.grid(row=0, column=2, sticky="nsew")
        self.game_labels.grid(row=0, column=3, sticky="nsew")
        self.game_right.grid(row=0, column=4, sticky="nsew")

        # create the center containers
        self.game_mid.grid_rowconfigure(2,weight=1)
        self.game_mid.grid_columnconfigure(0,weight=1)

        # create right labels for displaying top entropies
        self.game_labels.grid_rowconfigure(0,weight=1)
        self.game_labels.grid_columnconfigure(0,weight=1)
        self.entropies_container = ctk.CTkFrame(self.game_labels, width=95,height=100)
        self.entropies_container.grid(row=0,column=0)

        self.entropy_labels = {}
        self.populate_entropy_labels()

        self.div = ctk.CTkFrame(self.game_mid, width=20, height=20, fg_color="transparent")
        self.screen_container = ctk.CTkFrame(self.game_mid, width=250, height=190)
        self.vkeyboard_container = ctk.CTkFrame(self.game_mid, width=100, height=190)

        self.div.grid(row=0, column=0)
        self.screen_container.grid(row=1, column=0, pady=4)
        self.vkeyboard_container.grid(row=2, column=0, pady=8)

        self.build_screen_buttons()
        self.virtual_keyboard()
        self.delete = ctk.CTkButton(self.vkeyboard_container, text="DEL", height=40, width=40, command=self.erase_letter).grid(row=0,column=9)  
        

    def open_settings(self):
        if self.settings_window is None or not self.settings_window.winfo_exists():
            self.settings_window = Settings(self)
            self.settings_window.focus()
        else:
            self.settings_window.focus()  
    
    def build_screen_buttons(self):
        for i in range(6):
            for j in range(5):
                self.game_grid[(i,j)]= ctk.CTkButton(self.screen_container,text ="", width=40, height=40, command=partial(self.click_color_button,(i,j)), fg_color="#cac7c2")
                self.game_grid[(i,j)].grid(row=i,column=j)

    def populate_entropy_labels(self):
        for l in range(10):
            self.entropy_labels[l] = ctk.CTkLabel(self.entropies_container, text=l, width=70, height=30, padx=8, pady=4, font=self.main_font)
            self.entropy_labels[l].grid(row=l,column=0)
        
    def virtual_keyboard(self, option="Default"):
        if option == "Default":
            self.keyboard = [chr(x) for x in range(65,91)]
            self.keyboard.insert(14,'Ñ')
        elif option == "QWERTY":
            self.keyboard = "QWERTYUIOPASDFGHJKLÑZXCVBNM"
            self.keyboard = [l for l in self.keyboard]
        j=0
        for ind,button in enumerate(self.keyboard):
            if ind%9 == 0 and ind != 0:
                j = j+1
            self.vkeyboard_buttons[button] = ctk.CTkButton(self.vkeyboard_container, text=button, width=40, height=40, command=partial(self.click_vletter,button), font=self.main_font)
            self.vkeyboard_buttons[button].grid(row=j,column=ind%9)        
    
    def click_color_button(self, pos):
        color = self.game_grid[pos].cget("fg_color")
        if color=="#cac7c2":
            color="#97db46"
            self.color_matrix[pos] = 2
        elif color=="#97db46":
            color="#e8d32b"
            self.color_matrix[pos] = 1
        elif color=="#e8d32b":
            color="#cac7c2"
            self.color_matrix[pos] = 0
        self.game_grid[pos].configure(fg_color=color)

    def click_vletter(self,s):
        self.game_grid[self.pointer].configure(text=s, text_color='black')
        self.letter_matrix[self.pointer] = s
        i,j = self.pointer
        if j==4:
            i = i+1
        self.pointer = (i,(j+1)%5)

    def erase_letter(self):
        i, j = self.pointer
        if self.pointer == (0,0):
            return
        else:
            if j == 0:
                j = 4
                i = i-1
            else:
                j = j-1  
        self.pointer = (i,j)
        self.game_grid[self.pointer].configure(text="")
        self.letter_matrix[self.pointer] = ""

    def compute_entropies(self):
        i, j = self.pointer
        to_reduce = {"".join(self.letter_matrix[x]):tuple(self.color_matrix[x]) for x in range(i)}
        print("Reducing word_pool...")
        to_check = [k.lower() for k in to_reduce.keys()]
        exist = self.solver.check_existence(to_check)
        self.solver.reduce_pool(to_reduce)
        self.solver.compute_all()
        print("Reduced")

    def show_entropies(self):
        top_picks = self.solver.show_entropies()
        for ind, pick in enumerate(top_picks):
            self.entropy_labels[ind].configure(text=pick)

    def toggle_appearance_mode(self):
        if self.color_mode == 'dark':
            self.color_mode = 'light'
        else:
            self.color_mode = 'dark'

        ctk.set_appearance_mode(self.color_mode)


class Settings(ctk.CTkToplevel):
    def __init__(self, *args, **kwargs):
        self.dad = args[0]
        super().__init__(*args, **kwargs)
        self.geometry("400x300")
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.vkeyboard_values = ["Default", "QWERTY"]
        self.winfo_toplevel().title("Wordle Solver Settings")

        self.label = ctk.CTkLabel(self, text="Settings").grid(row=0,column=0)
        self.appearance_mode = ctk.CTkSwitch(self, text="Light Mode",onvalue="Dark", offvalue="Light", command=self.dad.toggle_appearance_mode).grid(row=1,column=0)
        self.vkeyboard_mode = ctk.CTkOptionMenu(self, values=self.vkeyboard_values, command=self.dad.virtual_keyboard, variable=self.dad.vkeyboard_option).grid(row=2,column=0)
        

    
if __name__ == "__main__":
    app = App()
    app.mainloop()