import tkinter as tk
import winreg
import sys
import os
from tkinter import ttk, messagebox
from src.operations import Calculation
from src.settings.datastore import CalculatorDataStore, CalculatorRegDataStore
from src.settings import CalculatorSettings
from src.utilities import ThemedMenubar, WindowsTitlebar, ThemedMenu


# noinspection PyMethodFirstArgAssignment
class CalculatorTk(tk.Tk, WindowsTitlebar):
    def __init__(self, *args, **kwargs) -> None:
        self.darkmode = kwargs.pop('darkmode', None)
        self.storehistory = kwargs.pop('storehistory', None)
        super().__init__(*args, **kwargs)
        self.attributes("-alpha", 1.00)
        self.withdraw()

        self.title("Calculator")
        self.size = (333, 408)
        self.resizable(False, False)
        self.settings_open = False
        self.settings_instance = None
        self.x_pos = (self.winfo_screenwidth() // 2) - (self.size[0] // 2)
        self.y_pos = (self.winfo_screenheight() // 2) - (self.size[1] // 2)
        self.geometry("{}x{}+{}+{}".format(self.size[0], self.size[1], self.x_pos, self.y_pos))

        self.datastore_info = CalculatorRegDataStore()
        self.database_is_ok = self.check_save_path() and self.datastore_info.save_settings
        self.database_preferences = CalculatorDataStore('preferences', self.datastore_info, self.database_is_ok)
        self.database_history = CalculatorDataStore('history', self.datastore_info, self.database_is_ok)

        if not self.storehistory:
            self.database_preferences.set_preferences('storehistory', f'1', 1) \
                if len(self.database_preferences.get_preferences('storehistory')) < 1 else None
        else:
            self.database_preferences.set_preferences('storehistory', f'{self.storehistory}', 1)
        if not self.darkmode:
            self.database_preferences.set_preferences('darkmode', f'2', 2) \
                if len(self.database_preferences.get_preferences('darkmode')) < 1 else None
        else:
            self.database_preferences.set_preferences('darkmode', f'{self.darkmode}', 2)
        self.selected_mode = 'system' if len(self.database_preferences.get_preferences('darkmode')) == 0 else 'dark' \
            if self.database_preferences.get_preferences('darkmode')[0][2] == '1' else 'light' \
            if self.database_preferences.get_preferences('darkmode')[0][2] == '0' else 'system'
        self.color = self.change_mode(self.selected_mode)
        self.protocol("WM_DELETE_WINDOW", self.close)

        self.open_file_icon_path = os.path.join(getattr(sys, '_MEIPASS', 'images'), 'open.png')
        self.open_file_icon_light_path = os.path.join(getattr(sys, '_MEIPASS', 'images'), 'open_l.png')
        self.calc_icon_path = os.path.join(getattr(sys, '_MEIPASS', 'images'), 'calc.ico')

        self.iconbitmap(self.calc_icon_path)

        self.style = ttk.Style()
        self.style.configure("CalcField.TLabel", height=1, font=("Consolas", 26),
                             background='#111111' if self.color != 'light' else 'white',
                             foreground='white' if self.color != 'light' else 'black', padding=(0, 10))
        self.style.configure("MenuSeparator.Horizontal.TSeparator", background='#000000')

        self.input_calculation = tk.StringVar(value="0")
        self.input_display_content = tk.StringVar(value="0 ")
        self.calc = Calculation(self, self.input_calculation, self.input_display_content)

        self.main_menu = ThemedMenubar(self, height=16, bg="#111111" if self.color != 'light' else 'white')
        self.main_menu.pack(side='top', fill='x')

        self.action_menu = ThemedMenu(self, bg='#171717', windowWidth=132, windowHeight=160, label_name="ActionMenu")

        self.bind("<Alt_L>", lambda event: self.main_menu.buttons[0].focus_set())

        self.action_menu.add_command(label="Delete", command=self.calc.delete, width=17, font=('Segoe UI', 10),
                                     padx=14, height=0, bg="#171717" if self.color != 'light' else '#DADADA',
                                     relief="sunken", fg='white' if self.color != 'light' else 'black', bd=0,
                                     hoverbackground="#131313" if self.color != 'light' else '#D0D0D0',
                                     activebackground="#0B0B0B" if self.color != 'light' else '#C5C5C5',
                                     activeforeground="white" if self.color != 'light' else "black")
        self.action_menu.add_command(label="Backspace", command=self.calc.backspace, width=17, font=('Segoe UI', 10),
                                     padx=14, height=0, bg="#171717" if self.color != 'light' else '#DADADA',
                                     relief="sunken", fg='white' if self.color != 'light' else 'black', bd=0,
                                     hoverbackground="#131313" if self.color != 'light' else '#D0D0D0',
                                     activebackground="#0B0B0B" if self.color != 'light' else '#C5C5C5',
                                     activeforeground="white" if self.color != 'light' else "black")
        self.action_menu.add_command(label="Remove Decimal", command=self.calc.remove_dot, width=17,
                                     font=('Segoe UI', 10), padx=14, height=0,
                                     bg="#171717" if self.color != 'light' else '#DADADA',
                                     relief="sunken", fg='white' if self.color != 'light' else 'black',
                                     bd=0, hoverbackground="#131313" if self.color != 'light' else '#D0D0D0',
                                     activebackground="#0B0B0B" if self.color != 'light' else '#C5C5C5',
                                     activeforeground="white" if self.color != 'light' else "black")
        self.action_menu.add_separator()

        self.number_menu = ThemedMenu(self, master_menu=self.action_menu, using_parent_master=True, height=16,
                                      windowWidth=62, windowHeight=260, bg="#131313", label_name="NumberMenu")
        for i in range(1, 10):
            self.number_menu.add_command(label=f"{i}", command=lambda i_=i: self.calc.action(i_), width=17,
                                         font=('Segoe UI', 10), height=0,
                                         bg="#171717" if self.color != 'light' else '#DADADA',
                                         relief="sunken", fg='white' if self.color != 'light' else "black",
                                         bd=0, hoverbackground="#131313" if self.color != 'light' else '#D0D0D0',
                                         activebackground="#0B0B0B" if self.color != 'light' else '#C5C5C5',
                                         activeforeground="white" if self.color != 'light' else "black")

        self.number_menu.add_command(label="0", command=lambda: self.calc.action(0), width=17, font=('Segoe UI', 10),
                                     height=0, bg="#171717" if self.color != 'light' else '#DADADA', relief="sunken",
                                     fg='white' if self.color != 'light' else "black", bd=0,
                                     hoverbackground="#131313" if self.color != 'light' else '#D0D0D0',
                                     activebackground="#0B0B0B" if self.color != 'light' else '#C5C5C5',
                                     activeforeground="white" if self.color != 'light' else "black")

        self.action_menu.add_cascade(label="Numbers" + " " * 10 + "▶", toplevel=self.number_menu, width=17,
                                     font=('Segoe UI', 10), padx=14, height=0,
                                     bg="#171717" if self.color != 'light' else '#DADADA',
                                     y_offset=-10, relief="sunken",
                                     fg='white' if self.color != 'light' else 'black', bd=0,
                                     hoverbackground="#131313" if self.color != 'light' else '#D0D0D0',
                                     activebackground="#0B0B0B" if self.color != 'light' else '#C5C5C5',
                                     activeforeground="white" if self.color != 'light' else "black")

        self.methods_menu = ThemedMenu(self, master_menu=self.action_menu, using_parent_master=True, height=16,
                                       windowWidth=62, windowHeight=260, bg="#131313", label_name="MethodsMenu")
        self.methods_menu.add_command(label="+", command=lambda: self.calc.set("plus"), width=17,
                                      font=('Segoe UI', 10), height=0,
                                      bg="#171717" if self.color != 'light' else '#DADADA',
                                      relief="sunken", fg='white' if self.color != 'light' else "black", bd=0,
                                      hoverbackground="#131313" if self.color != 'light' else '#D0D0D0',
                                      activebackground="#0B0B0B" if self.color != 'light' else '#C5C5C5',
                                      activeforeground="white" if self.color != 'light' else "black")
        self.methods_menu.add_command(label="-", command=lambda: self.calc.set("minus"), width=17,
                                      font=('Segoe UI', 10), height=0,
                                      bg="#171717" if self.color != 'light' else '#DADADA',
                                      relief="sunken", fg='white' if self.color != 'light' else "black",
                                      bd=0, hoverbackground="#131313" if self.color != 'light' else '#D0D0D0',
                                      activebackground="#0B0B0B" if self.color != 'light' else '#C5C5C5',
                                      activeforeground="white" if self.color != 'light' else "black")
        self.methods_menu.add_command(label="x", command=lambda: self.calc.set("multiply"), width=17,
                                      font=('Segoe UI', 10), height=0,
                                      bg="#171717" if self.color != 'light' else '#DADADA', relief="sunken",
                                      fg='white' if self.color != 'light' else "black", bd=0,
                                      hoverbackground="#131313" if self.color != 'light' else '#D0D0D0',
                                      activebackground="#0B0B0B" if self.color != 'light' else '#C5C5C5',
                                      activeforeground="white" if self.color != 'light' else "black")
        self.methods_menu.add_command(label="÷", command=lambda: self.calc.set("divide"), width=17,
                                      font=('Segoe UI', 10), height=0,
                                      bg="#171717" if self.color != 'light' else '#DADADA',
                                      relief="sunken", fg='white' if self.color != 'light' else "black",
                                      bd=0, hoverbackground="#131313" if self.color != 'light' else '#D0D0D0',
                                      activebackground="#0B0B0B" if self.color != 'light' else '#C5C5C5',
                                      activeforeground="white" if self.color != 'light' else "black")
        self.methods_menu.add_command(label="^", command=lambda: self.calc.set("power"), width=17,
                                      font=('Segoe UI', 10), height=0,
                                      bg="#171717" if self.color != 'light' else '#DADADA', relief="sunken",
                                      fg='white' if self.color != 'light' else "black", bd=0,
                                      hoverbackground="#131313" if self.color != 'light' else '#D0D0D0',
                                      activebackground="#0B0B0B" if self.color != 'light' else '#C5C5C5',
                                      activeforeground="white" if self.color != 'light' else "black")
        self.methods_menu.add_command(label="//", command=lambda: self.calc.set("perfect"), width=17,
                                      font=('Segoe UI', 10), height=0,
                                      bg="#171717" if self.color != 'light' else '#DADADA', relief="sunken",
                                      fg='white' if self.color != 'light' else "black", bd=0,
                                      hoverbackground="#131313" if self.color != 'light' else '#D0D0D0',
                                      activebackground="#0B0B0B" if self.color != 'light' else '#C5C5C5',
                                      activeforeground="white" if self.color != 'light' else "black")
        self.methods_menu.add_command(label="(", command=self.calc.open_paranthesis, width=17,
                                      font=('Segoe UI', 10), height=0,
                                      bg="#171717" if self.color != 'light' else '#DADADA', relief="sunken",
                                      fg='white' if self.color != 'light' else "black", bd=0,
                                      hoverbackground="#131313" if self.color != 'light' else '#D0D0D0',
                                      activebackground="#0B0B0B" if self.color != 'light' else '#C5C5C5',
                                      activeforeground="white" if self.color != 'light' else "black")
        self.methods_menu.add_command(label=")", command=self.calc.close_paranthesis, width=17,
                                      font=('Segoe UI', 10), height=0,
                                      bg="#171717" if self.color != 'light' else '#DADADA',
                                      relief="sunken", fg='white' if self.color != 'light' else "black",
                                      bd=0, hoverbackground="#131313" if self.color != 'light' else '#D0D0D0',
                                      activebackground="#0B0B0B" if self.color != 'light' else '#C5C5C5',
                                      activeforeground="white" if self.color != 'light' else "black")
        self.methods_menu.add_command(label="%", command=lambda: self.calc.set("modulus"), width=17,
                                      font=('Segoe UI', 10), height=0,
                                      bg="#171717" if self.color != 'light' else '#DADADA', relief="sunken",
                                      fg='white' if self.color != 'light' else "black", bd=0,
                                      hoverbackground="#131313" if self.color != 'light' else '#D0D0D0',
                                      activebackground="#0B0B0B" if self.color != 'light' else '#C5C5C5',
                                      activeforeground="white" if self.color != 'light' else "black")
        self.methods_menu.add_command(label=".", command=self.calc.dot, width=17, font=('Segoe UI', 10),
                                      height=0, bg="#171717" if self.color != 'light' else '#DADADA',
                                      relief="sunken", fg='white' if self.color != 'light' else "black",
                                      bd=0, hoverbackground="#131313" if self.color != 'light' else '#D0D0D0',
                                      activebackground="#0B0B0B" if self.color != 'light' else '#C5C5C5',
                                      activeforeground="white" if self.color != 'light' else "black")

        self.action_menu.add_cascade(label="Options" + " " * 12 + "▶", toplevel=self.methods_menu, width=17,
                                     font=('Segoe UI', 10), padx=14, height=0,
                                     bg="#171717" if self.color != 'light' else '#DADADA', y_offset=16,
                                     relief="sunken", fg='white' if self.color != 'light' else 'black',
                                     bd=0, hoverbackground="#131313" if self.color != 'light' else '#D0D0D0',
                                     activebackground="#0B0B0B" if self.color != 'light' else '#C5C5C5',
                                     activeforeground="white" if self.color != 'light' else "black")
        self.action_menu.add_separator()

        # self.action_menu.add_command(label=".", width=17, font=('Calibri', 10), height=0, bg="#171717",
        # relief="sunken", fg='white', bd=0, hoverbackground="#131313", activebackground="#0B0B0B",
        # activeforeground="white")
        self.action_menu.add_command(label="Equal (=)", command=self.calc.equal, width=17, font=('Segoe UI', 10),
                                     padx=14, height=0, bg="#171717" if self.color != 'light' else '#DADADA',
                                     relief="sunken", fg='white' if self.color != 'light' else 'black', bd=0,
                                     hoverbackground="#131313" if self.color != 'light' else '#D0D0D0',
                                     activebackground="#0B0B0B" if self.color != 'light' else '#C5C5C5',
                                     activeforeground="white" if self.color != 'light' else "black")

        self.settings_menu = ThemedMenu(self, bg='#171717', windowWidth=132, windowHeight=80, label_name="HelpMenu")

        self.settings_menu.add_command(label="Preferences...", command=self.open_preferences, width=17,
                                       font=('Segoe UI', 10), padx=14, height=0,
                                       bg="#171717" if self.color != 'light' else '#DADADA', relief="sunken",
                                       fg='white' if self.color != 'light' else 'black', bd=0,
                                       hoverbackground="#131313" if self.color != 'light' else '#D0D0D0',
                                       activebackground="#0B0B0B" if self.color != 'light' else '#C5C5C5',
                                       activeforeground="white" if self.color != 'light' else "black")
        self.settings_menu.add_command(label="History...", command=self.open_history, width=17, font=('Segoe UI', 10),
                                       padx=14, height=0, bg="#171717" if self.color != 'light' else '#DADADA',
                                       relief="sunken", fg='white' if self.color != 'light' else 'black', bd=0,
                                       hoverbackground="#131313" if self.color != 'light' else '#D0D0D0',
                                       activebackground="#0B0B0B" if self.color != 'light' else '#C5C5C5',
                                       activeforeground="white" if self.color != 'light' else "black")
        self.settings_menu.add_separator()
        self.settings_menu.add_command(label="About", command=self.open_about, width=17, font=('Segoe UI', 10),
                                       padx=14, height=0, bg="#171717" if self.color != 'light' else '#DADADA',
                                       relief="sunken", fg='white' if self.color != 'light' else 'black', bd=0,
                                       hoverbackground="#131313" if self.color != 'light' else '#D0D0D0',
                                       activebackground="#0B0B0B" if self.color != 'light' else '#C5C5C5',
                                       activeforeground="white" if self.color != 'light' else "black")

        self.action_cascade = self.main_menu.add_cascade_toplevel(
            label='Action', toplevel=self.action_menu, height=-15,
            activebackground='#202020' if self.color != 'light' else '#DFDFDF',
            bg='#131313' if self.color != 'light' else 'white', bd=0, highlightthickness=0, relief=tk.SUNKEN,
            activeforeground='white' if self.color != 'light' else 'black',
            fg='white' if self.color != 'light' else 'black',
            hoverbackground="#232323" if self.color != 'light' else '#F0F0F0', padx=3)
        self.action_menu.main_cascade_button = self.action_cascade
        self.action_cascade.grid(row=0, column=0)
        self.settings_cascade = self.main_menu.add_cascade_toplevel(
            label='Settings', toplevel=self.settings_menu, height=-15,
            activebackground='#202020' if self.color != 'light' else '#DFDFDF',
            bg='#131313' if self.color != 'light' else 'white', bd=0, highlightthickness=0, relief=tk.SUNKEN,
            x_offset=44, activeforeground='white' if self.color != 'light' else 'black',
            fg='white' if self.color != 'light' else 'black',
            hoverbackground="#232323" if self.color != 'light' else '#F0F0F0', padx=3)
        self.settings_menu.main_cascade_button = self.settings_cascade
        self.settings_cascade.grid(row=0, column=1)

        # self.action_menu = tk.Menu(self.main_menu.buttons[0], tearoff=0, bg='#202020', foreground='white',
        # disabledforeground='gray', activeforeground='white', activebackground='#303030')

        # self.action_number_menu = tk.Menu(tearoff=0, bg='#202020', foreground='white', disabledforeground='gray',
        # activeforeground='white', activebackground='#303030') self.action_number_menu.add_command(label='1')
        # self.action_number_menu.add_command(label='2') self.action_number_menu.add_command(label='3')
        # self.action_number_menu.add_command(label='4') self.action_number_menu.add_command(label='5')
        # self.action_number_menu.add_command(label='6') self.action_number_menu.add_command(label='7')
        # self.action_number_menu.add_command(label='8') self.action_number_menu.add_command(label='9')
        # self.action_number_menu.add_command(label='0')

        # self.action_menu.add_command(label='Delete')
        # self.action_menu.add_command(label='Backspace')
        # self.action_menu.add_command(label='Remove dot')
        # self.action_menu.add_separator()
        # self.numbers_cascade = self.action_menu.add_cascade(label="Numbers", menu=self.action_number_menu,
        # foreground='white')
        # self.action_menu.add_separator()
        # self.action_menu.add_command(label="Exit", command=self.destroy)

        # self.main_menu.edit_cascade(0, menu=self.action_menu)

        self.main_frame = tk.Frame(self, bg="#111111" if self.color != 'light' else '#F0F0F0')
        self.main_frame.pack(expand=True, fill='both')

        self.input_label = ttk.Label(self.main_frame, text="0", style="CalcField.TLabel", anchor='e',
                                     textvariable=self.input_display_content)
        self.input_label.place(relx=-1.0, y=0, relwidth=2.0, height=65)

        self.backspace_btn = tk.Button(self.main_frame, text='⌫', bg='#313131' if self.color != 'light' else '#F0F0F0',
                                       fg='white' if self.color != 'light' else 'black', padx=0, pady=2,
                                       font=('Consolas', 11), command=self.calc.backspace, bd=0, relief=tk.SUNKEN,
                                       activebackground="#2B2B2B" if self.color != 'light' else '#DFDFDF',
                                       activeforeground="white" if self.color != 'light' else 'black')
        self.backspace_btn.place(x=2, y=2)

        self.remove_dot_btn = tk.Button(self.main_frame, text='⁜',
                                        bg='#313131' if self.color != 'light' else '#F0F0F0',
                                        fg='white' if self.color != 'light' else 'black', padx=2, pady=1,
                                        font=('Consolas', 11), command=self.calc.remove_dot, bd=0, relief=tk.SUNKEN,
                                        activebackground="#2B2B2B" if self.color != 'light' else '#DFDFDF',
                                        activeforeground="white" if self.color != 'light' else 'black')
        self.remove_dot_btn.place(x=2, y=35)

        self.del_btn = tk.Button(self.main_frame, text='Del', bg='#313131' if self.color != 'light' else '#F0F0F0',
                                 fg='white' if self.color != 'light' else 'black', padx=4, pady=9,
                                 font=('Segoe UI', 15), width=3, command=self.calc.delete, bd=0, relief=tk.SUNKEN,
                                 activebackground="#2B2B2B" if self.color != 'light' else '#DFDFDF',
                                 activeforeground="white" if self.color != 'light' else 'black')
        self.del_btn.place(x=31, y=2)

        self.number_frame = tk.Frame(self.main_frame, bg="#111111" if self.color != 'light' else 'white')
        self.number_frame.pack(pady=(65, 0), side='left', anchor='n')
        self.number_btns = [[], [], [], []]

        for i in range(0, 3):
            for j in range(0, 4):
                if j == 0:
                    self.number_btns[i].append(None)
                    continue
                self.number_btns[i].append(tk.Button(self.number_frame, text=str(i * 3 + j),
                                                     bg='#313131' if self.color != 'light' else '#F0F0F0',
                                                     fg='white' if self.color != 'light' else 'black',
                                                     padx=22, pady=13, font=('Consolas', 18),
                                                     command=lambda i_=i, j_=j: self.calc.action(i_ * 3 + j_),
                                                     bd=0, relief=tk.SUNKEN,
                                                     activebackground="#2B2B2B" if self.color != 'light' else '#DFDFDF',
                                                     activeforeground="white" if self.color != 'light' else 'black'))
                self.number_btns[i][j].grid(row=i, column=j, sticky='news', padx=2, pady=2)

        self.number_btns[3].insert(1, tk.Button(self.number_frame, text='0',
                                                bg='#3A3A3A' if self.color != 'light' else '#F0F0F0',
                                                fg='white' if self.color != 'light' else 'black',
                                                padx=22, pady=13, font=('Consolas', 18),
                                                command=lambda: self.calc.action(0), bd=0, relief=tk.SUNKEN,
                                                activebackground="#2B2B2B" if self.color != 'light' else '#DFDFDF',
                                                activeforeground="white" if self.color != 'light' else 'black'))
        self.number_btns[3][0].grid(row=3, column=1, columnspan=2, sticky='news', padx=2, pady=2)

        self.plus_minus_pair = tk.Frame(self.number_frame, bg="#111111" if self.color != 'light' else 'white')
        self.plus_minus_pair.grid(padx=(0, 25), row=0, column=0, sticky='news')

        self.plus_btn = tk.Button(self.plus_minus_pair, text='+', bg='#313131' if self.color != 'light' else '#F0F0F0',
                                  fg='white' if self.color != 'light' else 'black', padx=26, pady=0,
                                  font=('Consolas', 15), command=lambda: self.calc.set("plus"), bd=0,
                                  relief=tk.SUNKEN, activebackground="#2B2B2B" if self.color != 'light' else '#DFDFDF',
                                  activeforeground="white" if self.color != 'light' else 'black')
        self.plus_btn.grid(row=0, column=0, sticky='news', padx=2, pady=2)

        self.minus_btn = tk.Button(self.plus_minus_pair, text='-', bg='#313131' if self.color != 'light' else '#F0F0F0',
                                   fg='white' if self.color != 'light' else 'black', padx=26, font=('Consolas', 15),
                                   command=lambda: self.calc.set("minus"), bd=0, relief=tk.SUNKEN,
                                   activebackground="#2B2B2B" if self.color != 'light' else '#DFDFDF',
                                   activeforeground="white" if self.color != 'light' else 'black')
        self.minus_btn.grid(row=1, column=0, sticky='news', padx=2, pady=2)

        self.multiply_divide_pair = tk.Frame(self.number_frame, bg="#111111" if self.color != 'light' else 'white')
        self.multiply_divide_pair.grid(row=1, column=0, sticky='news')

        self.multiply_btn = tk.Button(self.multiply_divide_pair, text='x',
                                      bg='#313131' if self.color != 'light' else '#F0F0F0',
                                      fg='white' if self.color != 'light' else 'black',
                                      padx=26, pady=0, font=('Consolas', 15), command=lambda: self.calc.set("multiply"),
                                      bd=0, relief=tk.SUNKEN,
                                      activebackground="#2B2B2B" if self.color != 'light' else '#DFDFDF',
                                      activeforeground="white" if self.color != 'light' else 'black')
        self.multiply_btn.grid(row=0, column=0, sticky='news', padx=2, pady=2)

        self.divide_btn = tk.Button(self.multiply_divide_pair, text='÷',
                                    bg='#313131' if self.color != 'light' else '#F0F0F0',
                                    fg='white' if self.color != 'light' else 'black', padx=26,
                                    font=('Consolas', 15), command=lambda: self.calc.set("divide"),
                                    bd=0, relief=tk.SUNKEN,
                                    activebackground="#2B2B2B" if self.color != 'light' else '#DFDFDF',
                                    activeforeground="white" if self.color != 'light' else 'black')
        self.divide_btn.grid(row=1, column=0, sticky='news', padx=2, pady=2)

        self.power_perfect_pair = tk.Frame(self.number_frame, bg="#111111" if self.color != 'light' else 'white')
        self.power_perfect_pair.grid(row=2, column=0, sticky='news')

        self.power_btn = tk.Button(self.power_perfect_pair, text='^',
                                   bg='#313131' if self.color != 'light' else '#F0F0F0',
                                   fg='white' if self.color != 'light' else 'black', padx=19,
                                   font=('Consolas', 16), command=lambda: self.calc.set("power"),
                                   bd=0, relief=tk.SUNKEN,
                                   activebackground="#2B2B2B" if self.color != 'light' else '#DFDFDF',
                                   activeforeground="white" if self.color != 'light' else 'black')
        self.power_btn.grid(row=1, column=0, sticky='news', padx=2, pady=2)

        self.perfect_btn = tk.Button(self.power_perfect_pair, text='//',
                                     bg='#313131' if self.color != 'light' else '#F0F0F0',
                                     fg='white' if self.color != 'light' else 'black', padx=19,
                                     font=('Consolas', 16), command=lambda: self.calc.set("perfect"),
                                     bd=0, relief=tk.SUNKEN,
                                     activebackground="#2B2B2B" if self.color != 'light' else '#DFDFDF',
                                     activeforeground="white" if self.color != 'light' else 'black')
        self.perfect_btn.grid(row=2, column=0, sticky='news', padx=2, pady=2)

        self.parenthesis_modulus_pair = tk.Frame(self.number_frame,
                                                 bg="#111111" if self.color != 'light' else 'white', bd=0,
                                                 relief=tk.SUNKEN)
        self.parenthesis_modulus_pair.grid(row=3, column=0, sticky='news')

        self.parenthesis_pair = tk.Frame(self.parenthesis_modulus_pair,
                                         bg="#111111" if self.color != 'light' else 'white', bd=0, relief=tk.SUNKEN)
        self.parenthesis_pair.grid(row=0, column=0, sticky='news')

        self.open_parenthesis_btn = tk.Button(self.parenthesis_pair, text='(',
                                              bg='#313131' if self.color != 'light' else '#F0F0F0',
                                              fg='white' if self.color != 'light' else 'black',
                                              padx=8, pady=1, font=('Consolas', 14), bd=0, relief=tk.SUNKEN,
                                              command=self.calc.open_paranthesis,
                                              activebackground="#2B2B2B" if self.color != 'light' else '#DFDFDF',
                                              activeforeground="white" if self.color != 'light' else 'black')
        self.open_parenthesis_btn.grid(row=0, column=0, sticky='news', padx=2, pady=2)

        self.close_parenthesis_btn = tk.Button(self.parenthesis_pair, text=')',
                                               bg='#313131' if self.color != 'light' else '#F0F0F0',
                                               fg='white' if self.color != 'light' else 'black', padx=8, pady=1,
                                               font=('Consolas', 14), bd=0, relief=tk.SUNKEN,
                                               command=self.calc.close_paranthesis,
                                               activebackground="#2B2B2B" if self.color != 'light' else '#DFDFDF',
                                               activeforeground="white" if self.color != 'light' else 'black')
        self.close_parenthesis_btn.grid(row=0, column=1, sticky='news', padx=2, pady=2)

        self.modulus_btn = tk.Button(self.parenthesis_modulus_pair, text='Mod(%)',
                                     bg='#313131' if self.color != 'light' else '#F0F0F0',
                                     fg='white' if self.color != 'light' else 'black', padx=1, pady=1,
                                     font=('Consolas', 14), bd=0, relief=tk.SUNKEN,
                                     command=lambda: self.calc.set("modulus"),
                                     activebackground="#2B2B2B" if self.color != 'light' else '#DFDFDF',
                                     activeforeground="white" if self.color != 'light' else 'black')
        self.modulus_btn.grid(row=1, column=0, sticky='news', padx=2, pady=2)

        self.equal_dot_pair = tk.Frame(self.number_frame, bg="#111111" if self.color != 'light' else 'white')
        self.equal_dot_pair.grid(row=3, column=3, sticky='news')

        self.dot_btn = tk.Button(self.equal_dot_pair, text='.', bg='#313131' if self.color != 'light' else '#F0F0F0',
                                 fg='white' if self.color != 'light' else 'black', padx=28, pady=1,
                                 font=('Consolas', 14), command=self.calc.dot, bd=0, relief=tk.SUNKEN,
                                 activebackground="#2B2B2B" if self.color != 'light' else '#DFDFDF',
                                 activeforeground="white" if self.color != 'light' else 'black')
        self.dot_btn.grid(row=0, column=0, sticky='news', padx=2, pady=2)

        self.equal_btn = tk.Button(self.equal_dot_pair, text='=', bg='#212121' if self.color != 'light' else '#F0F0F0',
                                   fg='white' if self.color != 'light' else 'black', padx=28, pady=1,
                                   font=('Consolas', 14), command=self.calc.equal, bd=0, relief=tk.SUNKEN,
                                   activebackground="#2B2B2B" if self.color != 'light' else '#DFDFDF',
                                   activeforeground="white" if self.color != 'light' else 'black')
        self.equal_btn.grid(row=1, column=0, sticky='news', padx=2, pady=2)

        self.focus_force()
        self.attributes("-alpha", 1.00)
        self.deiconify()
        # self.open_preferences()

    def restart_app(self, open_preferences=False, darkmode=None, storehistory=None):
        try:
            self.destroy()
        except tkinter.TclError:
            pass
        self = CalculatorTk(darkmode=darkmode, storehistory=storehistory)

        self.open_preferences() if open_preferences else None
        self.mainloop()

    def change_mode(self, mode: str):
        if mode == 'system':
            reg_path = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize'
            try:
                reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path)
                light, _ = winreg.QueryValueEx(reg_key, "AppsUseLightTheme")
                if light:
                    return self.change_mode('light')
                else:
                    return self.change_mode('dark')
            except FileNotFoundError:
                return self.change_mode('dark')

        elif mode == 'dark':
            self._dark_title_bar()

        elif mode == 'light':
            self._light_title_bar()
        return mode

    def check_save_path(self):
        try:
            os.makedirs(self.datastore_info.save_path, exist_ok=True)
            if not os.path.exists(os.path.expandvars(self.datastore_info.save_path)):
                print(os.path.expandvars(self.database_info.save_path))
                messagebox.showwarning(message="The specified save path does not exist. Some preferences will be "
                                               "stored in memory.", title="Calculator Error")
                return False
            os.mkdir(os.path.join(os.path.expandvars(self.datastore_info.save_path), 'tes'))
            os.rmdir(os.path.join(os.path.expandvars(self.datastore_info.save_path), 'tes'))
        except Exception as e:
            print(e)
            messagebox.showwarning(message="We are unable to access the save path. Some preferences will be stored in "
                                           "memory.", title="Calculator Error")
            return False
        return True

    def close(self):
        self.database_preferences.close()
        self.database_history.close()
        self.destroy()

    def open_about(self):
        if self.settings_open:
            self.settings_instance.focus_force()
            self.settings_instance.switch_tab('about')
            return
        return CalculatorSettings(self, tab='about')

    def open_history(self):
        if self.settings_open:
            self.settings_instance.focus_force()
            self.settings_instance.switch_tab('history')
            return
        return CalculatorSettings(self, tab='history')

    def open_preferences(self):
        if self.settings_open:
            self.settings_instance.focus_force()
            self.settings_instance.switch_tab('preferences')
            return
        return CalculatorSettings(self, tab='preferences')
