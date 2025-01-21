import tkinter as tk
import webbrowser
import sqlite3
import winreg
import shutil
import json
import math
import sys
import os
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
from utilities import ThemedMenubar, WindowsTitlebar, ThemedMenu, wait_for_file


# noinspection PyTypeChecker
class CalculatorSettings(tk.Toplevel, WindowsTitlebar):
    """
    Calculator - Version v1.0.0
    Coded and published by SrpCD.
    
    Python Version: {}.{}.{} x{}
    Tkinter Version: {}
    """
    
    def __init__(self, master=None, *args, **kwargs) -> None:
        self.open_tab = kwargs.pop("tab", "preferences")
        self.__doc__ = self.__doc__.format(sys.version_info[0], sys.version_info[1], sys.version_info[2],
                                           "64" if sys.maxsize > 2**32 else "32", tk.TclVersion)
        
        super().__init__(master, *args, **kwargs)
        self.master.settings_open = True
        self.master.settings_instance = self
        self.attributes("-alpha", 1.00)
        self.withdraw()
        
        self.title("Calculator Settings")
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.size = (333, 208)
        self.resizable(False, False)
        
        self.transient(master)
        self.color = self.change_mode(self.master.selected_mode)
        self.bind("<Map>", lambda event: setattr(self, 'color', self.change_mode(self.master.selected_mode)))
        self.x_pos = (self.winfo_screenwidth() // 2) - (self.size[0] // 2)
        self.y_pos = (self.winfo_screenheight() // 2) - (self.size[1] // 2)
        self.geometry("{}x{}+{}+{}".format(self.size[0], self.size[1], self.x_pos, self.y_pos))
        self.iconbitmap(os.path.join(getattr(sys, '_MEIPASS', 'images'), 'calc.ico'))
        self.config(bg="#111111" if self.color != 'light' else '#F0F0F0')
        
        self.github_url = "https://github.com/srpcd/calculator-tk"
        
        self.history_selected_frames = []
        self.history_visible_selected_frames = []
        
        self.main_frame = tk.Frame(self, bg=self['bg'])
        self.main_frame.pack(expand=True, fill='both')
        
        self.tab = self.open_tab
        
        self.tab_preferences = tk.Button(self, text='Preferences', relief=tk.SUNKEN, bd=0, highlightthickness=0,
                                         bg="#171717" if self.color != 'light' else '#D3D3D3',
                                         fg='white' if self.color != 'light' else 'black', font=("Segoe UI", 10),
                                         activebackground="#2A2A2A" if self.color != 'light' else '#E6E6E6',
                                         activeforeground="white" if self.color != 'light' else 'black', padx=2, pady=2,
                                         command=lambda: self.switch_tab('preferences'))
        self.tab_preferences.place(x=0, y=0, relwidth=0.3)
        
        self.tab_history = tk.Button(self, text='History', relief=tk.SUNKEN, bd=0, highlightthickness=0,
                                     bg="#171717" if self.color != 'light' else '#D3D3D3',
                                     fg='white' if self.color != 'light' else 'black', font=("Segoe UI", 10),
                                     activebackground="#2A2A2A" if self.color != 'light' else '#E6E6E6',
                                     activeforeground="white" if self.color != 'light' else 'black',
                                     padx=2, pady=2, command=lambda: self.switch_tab('history'))
        self.tab_history.place(x=7, y=0, relwidth=0.4, relx=0.3, width=-7)
        
        self.tab_about = tk.Button(self, text='About', relief=tk.SUNKEN, bd=0, highlightthickness=0,
                                   bg="#171717" if self.color != 'light' else '#D3D3D3',
                                   fg='white' if self.color != 'light' else 'black', font=("Segoe UI", 10),
                                   activebackground="#2A2A2A" if self.color != 'light' else '#E6E6E6',
                                   activeforeground="white" if self.color != 'light' else 'black',
                                   padx=2, pady=2, command=lambda: self.switch_tab('about'))
        self.tab_about.place(x=7, y=0, relwidth=0.3, relx=0.7, width=-7)
        
        self.box_frame = tk.Frame(self.main_frame, bg="#2A2A2A" if self.color != 'light' else '#D0D0D0')
        self.box_frame.pack(expand=True, fill='both', pady=(26, 0))
        
        self.preferences_frame = tk.Frame(self.box_frame, bg="#2A2A2A" if self.color != 'light' else '#E6E6E6')
        self.preferences_frame.pack(expand=True, fill='both')
        
        self.preferences_name = tk.Label(self.preferences_frame, bg="#2A2A2A" if self.color != 'light' else '#E6E6E6',
                                         fg='white' if self.color != 'light' else 'black', text="Preferences",
                                         justify=tk.LEFT, font=("Calibri", 11))
        self.preferences_name.place(x=20, y=10)
        
        # print(self.master.database_preferences.get_preferences('storehistory'))
        # print(self.master.database_preferences.get_preferences('darkmode'))
        
        self.preferences_save_history_var = tk.IntVar(
            value=self.master.database_preferences.get_preferences('storehistory')[0][2])
        self.preferences_save_history = tk.Checkbutton(
            self.preferences_frame, bg="#2A2A2A" if self.color != 'light' else '#E6E6E6',
            text="Save and keep your past calculations in history.",
            fg='white' if self.color != 'light' else 'black',
            variable=self.preferences_save_history_var, onvalue=1,
            offvalue=0, font=("Calibri", 10),
            activebackground="#2A2A2A" if self.color != 'light' else '#E6E6E6',
            activeforeground="white" if self.color != 'light' else 'black',
            selectcolor="#2A2A2A" if self.color != 'light' else '#E6E6E6',
            command=lambda: (
                self.master.database_preferences.set_preferences(
                    'storehistory', f'{self.preferences_save_history_var.get()}', 1),
                self.preferences_apply_btn.config(state='normal')))
        self.preferences_save_history.place(x=20, y=35)
        
        self.preferences_save_settings_var = tk.IntVar(value=0 if self.master.datastore_info.save_settings < 1 else 1)
        self.preferences_save_settings = tk.Checkbutton(
            self.preferences_frame, bg="#2A2A2A" if self.color != 'light' else '#E6E6E6',
            text="Save preferences and history on disk.",
            fg='white' if self.color != 'light' else 'black',
            variable=self.preferences_save_settings_var,
            onvalue=1, offvalue=0, font=("Calibri", 10),
            activebackground="#2A2A2A" if self.color != 'light' else '#E6E6E6',
            activeforeground="white" if self.color != 'light' else 'black',
            selectcolor="#2A2A2A" if self.color != 'light' else '#E6E6E6',
            command=lambda: self.preferences_apply_btn.config(state='normal'))
        self.preferences_save_settings.place(x=20, y=60)
        
        self.preferences_save_location_var = tk.StringVar(value=self.master.datastore_info.save_path)
        self.preferences_save_location_label = tk.Label(self.preferences_frame, text="Data Folder: ",
                                                        bg="#2A2A2A" if self.color != 'light' else '#E6E6E6',
                                                        fg='white' if self.color != 'light' else 'black',
                                                        font=('Calibri', 10))
        self.preferences_save_location_label.place(x=20, y=88)
        
        self.preferences_save_location_entry = tk.Entry(
            self.preferences_frame, background="#000000" if self.color != 'light' else '#D3D3D3',
            foreground='white' if self.color != 'light' else 'black', font=("Calibri", 10),
            width=26, bd=0, highlightthickness=0, insertbackground='white' if self.color != 'light' else 'black',
            selectbackground="#333333", textvariable=self.preferences_save_location_var)
        self.preferences_save_location_entry.place(x=97, y=88, height=22)
        self.preferences_save_location_entry.bind(
            "<Key>", lambda event: self.preferences_apply_btn.config(state='normal'))
        
        if self.color != 'light':
            self.preferences_open_file_logo_image_pil = Image.open(self.master.open_file_icon_path).resize((13, 13))
            self.preferences_open_file_logo_image = ImageTk.PhotoImage(self.preferences_open_file_logo_image_pil)
        else:
            self.preferences_open_file_logo_image_pil = (Image.open(self.master.open_file_icon_light_path).
                                                         resize((13, 13)))
            self.preferences_open_file_logo_image = ImageTk.PhotoImage(self.preferences_open_file_logo_image_pil)
        
        self.preferences_save_location_open_file = tk.Button(
            self.preferences_frame, background="#000000" if self.color != 'light' else '#D3D3D3',
            image=self.preferences_open_file_logo_image, bd=0, highlightthickness=0, relief=tk.SUNKEN,
            activebackground="#232323" if self.color != 'light' else '#D7D7D7',
            activeforeground="white" if self.color != 'light' else 'black',
            command=self.preferences_open_file_location)
        self.preferences_save_location_open_file.place(x=285, y=88, width=22, height=22)
        
        self.preferences_use_dark_mode_var = tk.IntVar(
            value=int(self.master.database_preferences.get_preferences('darkmode')[0][2]))
        
        self.preferences_use_dark_mode = tk.Radiobutton(
            self.preferences_frame, bg="#2A2A2A" if self.color != 'light' else '#E6E6E6',
            text="Dark Mode", fg='white' if self.color != 'light' else 'black',
            variable=self.preferences_use_dark_mode_var, value=1,
            font=("Calibri", 10),
            activebackground="#2A2A2A" if self.color != 'light' else '#E6E6E6',
            activeforeground="white" if self.color != 'light' else 'black',
            selectcolor="#2A2A2A" if self.color != 'light' else '#E6E6E6',
            command=lambda: (
                self.master.database_preferences.set_preferences(
                    'darkmode', f'{self.preferences_use_dark_mode_var.get()}', 2),
                self.preferences_apply_btn.config(state='normal')))
        self.preferences_use_dark_mode.place(x=20, y=113)
        self.preferences_use_light_mode = tk.Radiobutton(
            self.preferences_frame, bg="#2A2A2A" if self.color != 'light' else '#E6E6E6',
            text="Light Mode", fg='white' if self.color != 'light' else 'black',
            variable=self.preferences_use_dark_mode_var, value=0,
            font=("Calibri", 10), activebackground="#2A2A2A" if self.color != 'light' else '#E6E6E6',
            activeforeground="white" if self.color != 'light' else 'black',
            selectcolor="#2A2A2A" if self.color != 'light' else '#E6E6E6',
            command=lambda: (
                self.master.database_preferences.set_preferences(
                    'darkmode', f'{self.preferences_use_dark_mode_var.get()}', 2),
                self.preferences_apply_btn.config(state='normal')))
        self.preferences_use_light_mode.place(x=110, y=113)
        self.preferences_use_system = tk.Radiobutton(
            self.preferences_frame, bg="#2A2A2A" if self.color != 'light' else '#E6E6E6', text="System Default",
            fg='white' if self.color != 'light' else 'black', variable=self.preferences_use_dark_mode_var, value=2,
            font=("Calibri", 10), activebackground="#2A2A2A" if self.color != 'light' else '#E6E6E6',
            activeforeground="white" if self.color != 'light' else 'black',
            selectcolor="#2A2A2A" if self.color != 'light' else '#E6E6E6',
            command=lambda: (
                self.master.database_preferences.set_preferences(
                    'darkmode', f'{self.preferences_use_dark_mode_var.get()}', 2),
                self.preferences_apply_btn.config(state='normal')))
        self.preferences_use_system.place(x=200, y=113)
        
        # self.preferences_backup_data = tk.Button(
        # self.preferences_frame, bg="#000000" if self.color != 'light' else '#D3D3D3',
        # text="Backup Data", fg='white' if self.color != 'light' else 'black', bd=0, highlightthickness=0,
        # relief=tk.SUNKEN, font=("Calibri", 10), activebackground="#232323" if self.color != 'light' else '#D7D7D7',
        # activeforeground="white" if self.color != 'light' else 'black', padx=6, pady=2)
        # self.preferences_backup_data.place(x=24, y=145)
        
        self.preferences_reset_to_default_btn = tk.Button(
            self.preferences_frame, text='Reset to Default', relief=tk.SUNKEN, bd=0, highlightthickness=0,
            bg="#000000" if self.color != 'light' else '#D3D3D3',
            fg='white' if self.color != 'light' else "black",
            font=("Calibri", 10), padx=9, pady=2,
            activebackground="#232323" if self.color != 'light' else '#D7D7D7',
            activeforeground="white" if self.color != 'light' else "black", command=lambda: (
                self.master.database_preferences.set_preferences('storehistory', f'1', 1),
                self.master.database_preferences.set_preferences('darkmode', f'2', 2),
                self.preferences_save_history_var.set(
                    self.master.database_preferences.get_preferences('storehistory')[0][2]),
                self.preferences_use_dark_mode_var.set(
                    self.master.database_preferences.get_preferences('darkmode')[0][2]),
                self.preferences_save_location_var.set(
                    os.path.join(os.path.expandvars("%LOCALAPPDATA%\\calculator-tk"))),
                self.preferences_apply_btn.config(state='normal')))

        self.preferences_reset_to_default_btn.place(x=136, y=145)

        # bg="#000000" if self.color != 'light' else '#D3D3D3', activebackground="#232323" if self.color != 'light'
        # else '#D7D7D7', activeforeground="white" if self.color != 'light' else "black", fg='white' if self.color !=
        # 'light' else 'black'

        self.preferences_apply_btn = tk.Button(self.preferences_frame, text='Apply', relief=tk.SUNKEN, bd=0,
                                               highlightthickness=0,
                                               bg="#000000" if self.color != 'light' else '#D3D3D3',
                                               fg='white' if self.color != 'light' else 'black',
                                               font=("Calibri", 10), padx=9, pady=2,
                                               activebackground="#232323" if self.color != 'light' else '#D7D7D7',
                                               activeforeground="white" if self.color != 'light' else "black",
                                               state='disabled', command=self.apply)
        self.preferences_apply_btn.place(x=256, y=145)
        
        self.history_frame = tk.Frame(self.box_frame, bg="#2A2A2A" if self.color != 'light' else '#E6E6E6')
        self.history_frame.pack(expand=True, fill='both')
        
        self.history_name = tk.Label(self.history_frame, bg="#2A2A2A" if self.color != 'light' else '#E6E6E6',
                                     fg='white' if self.color != 'light' else 'black', text="History",
                                     justify=tk.LEFT, font=("Calibri", 11))

        self.history_items_selected = tk.StringVar(value="0 items selected")
        self.history_selected_items = tk.Label(self.history_frame, bg="#2A2A2A" if self.color != 'light' else '#E6E6E6',
                                               fg='white' if self.color != 'light' else 'black',
                                               textvariable=self.history_items_selected, justify=tk.RIGHT,
                                               font=("Calibri", 11))

        self.history_max_page = 1
        self.history_starter = True
        self.history_current_page = tk.StringVar(value='1')
        
        self.history_old_calculations_frame = tk.Frame(self.history_frame,
                                                       bg="#3A3A3A" if self.color != 'light' else '#D6D6D6', height=104)
        self.history_old_calculations_inner = tk.Frame(self.history_old_calculations_frame,
                                                       bg="#3A3A3A" if self.color != 'light' else '#D6D6D6')
        
        self.history_no_history_msg = tk.Label(self.history_frame,
                                               text="History is currently disabled.\nPlease enable it from "
                                                    "preferences.", justify=tk.LEFT,
                                               bg="#2A2A2A" if self.color != 'light' else '#E6E6E6',
                                               fg="white" if self.color != 'light' else 'black',
                                               font=("Calibri", 12))
        self.history_no_history_ok_btn = tk.Button(self.history_frame, text='OK', relief=tk.SUNKEN, bd=0,
                                                   highlightthickness=0, font=("Calibri", 10), padx=27, pady=2,
                                                   bg="#000000" if self.color != 'light' else '#D3D3D3',
                                                   activebackground="#232323" if self.color != 'light' else '#D7D7D7',
                                                   activeforeground="white" if self.color != 'light' else "black",
                                                   fg='white' if self.color != 'light' else 'black',
                                                   command=self.close)
        self.history_old_calculations = []
        
        self.history_prev_btn = tk.Button(self.history_frame, text=' < ', relief=tk.SUNKEN, bd=0,
                                          highlightthickness=0, font=("Calibri", 10), padx=2, pady=2,
                                          bg="#000000" if self.color != 'light' else '#D3D3D3',
                                          activebackground="#232323" if self.color != 'light' else '#D7D7D7',
                                          activeforeground="white" if self.color != 'light' else "black",
                                          fg='white' if self.color != 'light' else 'black',
                                          state='disabled', command=self.prev_page)
        
        self.history_page_validation = self.register(self.validate_page_entry)
        
        self.history_page = tk.Entry(self.history_frame, insertbackground='white' if self.color != 'light' else 'black',
                                     background="#000000" if self.color != 'light' else '#D3D3D3',
                                     foreground='white' if self.color != 'light' else 'black', font=("Calibri", 10),
                                     justify=tk.CENTER, width=3, bd=0, highlightthickness=0,
                                     selectbackground="#333333", textvariable=self.history_current_page)
        
        self.history_next_btn = tk.Button(self.history_frame, text=' > ', relief=tk.SUNKEN, bd=0, highlightthickness=0,
                                          font=("Calibri", 10), padx=2, pady=2,
                                          bg="#000000" if self.color != 'light' else '#D3D3D3',
                                          activebackground="#232323" if self.color != 'light' else '#D7D7D7',
                                          activeforeground="white" if self.color != 'light' else "black",
                                          fg='white' if self.color != 'light' else 'black',
                                          command=self.next_page, state='disabled')
        
        self.history_clear_btn = tk.Button(self.history_frame, text='Clear', relief=tk.SUNKEN, bd=0,
                                           highlightthickness=0, font=("Calibri", 10), padx=9, pady=2,
                                           bg="#000000" if self.color != 'light' else '#D3D3D3',
                                           activebackground="#232323" if self.color != 'light' else '#D7D7D7',
                                           activeforeground="white" if self.color != 'light' else "black",
                                           fg='white' if self.color != 'light' else 'black', state='disabled',
                                           command=lambda: (
                                               self.master.database_history.clear_history(
                                                   self.history_old_calculations, self.history_clear_btn),
                                               self.history_apply_btn.config(state=tk.NORMAL),
                                               self.history_selected_frames.clear(),
                                               self.switch_tab('history'),
                                               self.history_open_btn.config(state=tk.DISABLED),
                                               self.history_remove_btn.config(state=tk.DISABLED),
                                               self.history_items_selected.set(
                                                   f"{len(self.history_selected_frames)} items selected")))
        if self.master.database_history.get_history_calculations():
            self.history_clear_btn.config(state='normal')
        
        self.history_open_btn = tk.Button(self.history_frame, text='Open', relief=tk.SUNKEN, bd=0,
                                          highlightthickness=0,
                                          font=("Calibri", 10), padx=9, pady=2,
                                          bg="#000000" if self.color != 'light' else '#D3D3D3',
                                          activebackground="#232323" if self.color != 'light' else '#D7D7D7',
                                          activeforeground="white" if self.color != 'light' else "black",
                                          fg='white' if self.color != 'light' else 'black', state='disabled',
                                          command=self.open_history_frame)
        
        self.history_remove_btn = tk.Button(self.history_frame, text='Remove', relief=tk.SUNKEN, bd=0,
                                            highlightthickness=0, font=("Calibri", 10), padx=9, pady=2,
                                            bg="#000000" if self.color != 'light' else '#D3D3D3',
                                            activebackground="#232323" if self.color != 'light' else '#D7D7D7',
                                            activeforeground="white" if self.color != 'light' else "black",
                                            fg='white' if self.color != 'light' else 'black', state='disabled',
                                            command=self.remove_frames)
        
        self.history_apply_btn = tk.Button(self.history_frame, text='Apply', relief=tk.SUNKEN, bd=0,
                                           highlightthickness=0, font=("Calibri", 10), padx=9, pady=2,
                                           bg="#000000" if self.color != 'light' else '#D3D3D3',
                                           activebackground="#232323" if self.color != 'light' else '#D7D7D7',
                                           activeforeground="white" if self.color != 'light' else "black",
                                           fg='white' if self.color != 'light' else 'black', state='disabled',
                                           command=lambda: self.master.database_history.apply(self.history_apply_btn))
        
        self.about_frame = tk.Frame(self.box_frame, bg="#2A2A2A" if self.color != 'light' else '#E6E6E6')
        self.about_frame.pack(expand=True, fill='both')
        
        self.about_name = tk.Label(self.about_frame, bg="#2A2A2A" if self.color != 'light' else '#E6E6E6',
                                   fg='white' if self.color != 'light' else 'black', text=self.__doc__,
                                   justify=tk.LEFT, font=("Calibri", 11))
        self.about_name.place(x=20, y=0)
        
        self.app_logo_image = Image.open(self.master.calc_icon_path).resize((70, 70))
        self.app_logo = ImageTk.PhotoImage(self.app_logo_image)
        
        self.about_app_logo = tk.Label(self.about_frame, image=self.app_logo,
                                       bg="#2A2A2A" if self.color != 'light' else '#E6E6E6')
        self.about_app_logo.place(relx=1, x=-30, y=20, anchor='ne')
        
        self.about_github_btn = tk.Button(self.about_frame, text='GitHub', relief=tk.SUNKEN, bd=0,
                                          highlightthickness=0, bg="#000000" if self.color != 'light' else '#D3D3D3',
                                          fg='white' if self.color != 'light' else 'black', font=("Calibri", 10),
                                          padx=6, pady=2,
                                          activebackground="#232323" if self.color != 'light' else '#D7D7D7',
                                          activeforeground="white" if self.color != 'light' else 'black',
                                          command=lambda: webbrowser.open(self.github_url))
        self.about_github_btn.place(x=23, y=130)
        
        # insertbackground='white' if self.color != 'light' else 'black', background="#000000" if self.color != 'light'
        # else '#D3D3D3', foreground='white' if self.color != 'light' else 'black'
        
        self.about_github_link = tk.Entry(self.about_frame,
                                          disabledbackground="#000000" if self.color != 'light' else '#D3D3D3',
                                          disabledforeground='white' if self.color != 'light' else 'black',
                                          font=("Calibri", 10), width=31, bd=0, highlightthickness=0,
                                          insertbackground='white' if self.color != 'light' else 'black')
        self.about_github_link.insert(0, self.github_url)
        self.about_github_link.config(state=tk.DISABLED)
        self.about_github_link.place(x=83, y=130, height=22)
        
        self.switch_tab(self.open_tab)
        self.focus_force()
        self.attributes("-alpha", 1.00)
        self.deiconify()
        
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
            if not os.path.exists(os.path.expandvars(self.preferences_save_location_var.get())):
                messagebox.showwarning(message="The specified save path does not exist.", title="Calculator Error")
                return False
            os.mkdir(os.path.join(os.path.expandvars(self.preferences_save_location_var.get()), 'tes'))
            os.rmdir(os.path.join(os.path.expandvars(self.preferences_save_location_var.get()), 'tes'))
        except Exception as e:
            messagebox.showwarning(message=f"We are unable to access the save path. "
                                           f"Traceback {e.__class__.__name__}: {e}", title="Calculator Error")
            return False
        return True
        
    def apply(self):
        if self.check_save_path():
            if self.master.datastore_info.save_settings != self.preferences_save_settings_var.get():
                successful_path = self.master.datastore_info.set_save_path(self.preferences_save_location_var.get())
                successful_save_setting = self.master.datastore_info.set_save_settings(
                    self.preferences_save_settings_var.get())
                if not (successful_path or successful_save_setting):
                    messagebox.showwarning(message="We were unable to change some settings from the data paths. "
                                                   "Please check your computer if you have any registry keys in use.",
                                           title="Calculator Error")
                if ((not self.master.database_history.using_memory) or
                        (not self.master.database_preferences.using_memory)):
                    if hasattr(self.master.database_preferences, 'conn'):
                        self.master.database_preferences.apply(self.preferences_apply_btn)
                    if hasattr(self.master.database_history, 'conn'):
                        self.master.database_history.apply(self.history_apply_btn)

                    self.master.database_preferences.close() \
                        if hasattr(self.master.database_preferences, 'conn') else None
                    self.master.database_history.close() \
                        if hasattr(self.master.database_history, 'conn') else None
                    
                    user_input = messagebox.askyesno(message="Do you want to keep your settings save?",
                                                     title="File Removal")
                    if not user_input:
                        try:
                            wait_for_file(self.master.database_history.database_file_name, 5, 0.5)
                            wait_for_file(self.master.database_preferences.database_file_name, 5, 0.5)
                            os.remove(self.master.database_history.database_file_name) \
                                if os.path.exists(self.master.database_history.database_file_name) else None
                            os.remove(self.master.database_preferences.database_file_name) \
                                if os.path.exists(self.master.database_preferences.database_file_name) else None
                            os.rmdir(self.master.database_preferences.database_folder) \
                                if not os.listdir(self.master.database_preferences.database_folder) else None
                        except Exception as e:
                            messagebox.showerror(message=f"An error occurred when deleting your settings: {e}",
                                                 title="File Removal")
                elif (self.preferences_save_settings_var.get() == 1 and
                      self.master.datastore_info.save_settings != self.preferences_save_settings_var.get()):
                    if hasattr(self.master.database_preferences, 'conn'):
                        self.master.database_preferences.apply(self.preferences_apply_btn)
                    if hasattr(self.master.database_history, 'conn'):
                        self.master.database_history.apply(self.history_apply_btn)

                    preferences_path = os.path.join(self.preferences_save_location_var.get(), 'preferences.db')
                    history_path = os.path.join(self.preferences_save_location_var.get(), 'history.db')

                    try:
                        self.master.database_history.cur.executemany(f"""
                            ATTACH DATABASE '{preferences_path}' AS preferences;
                            ATTACH DATABASE '{history_path}' AS history;
                        """)

                        if hasattr(self.master.database_preferences, 'conn'):
                            self.master.database_preferences.cur.execute(
                                "SELECT name FROM sqlite_master WHERE type='table'")
                            tables = self.master.database_history.cur.fetchall()

                            for table in tables:
                                table_name = table[0]
                                self.master.database_history.cur.execute(
                                    f"CREATE TABLE preferences.{table_name} AS SELECT * FROM {table_name};")
                            self.master.database_preferences.conn.commit()

                        if hasattr(self.master.database_history, 'conn'):
                            self.master.database_history.cur.execute(
                                "SELECT name FROM sqlite_master WHERE type='table';")
                            tables = self.master.database_history.cur.fetchall()

                            for table in tables:
                                table_name = table[0]
                                self.master.database_history.cur.execute(
                                    f"CREATE TABLE history.{table_name} AS SELECT * FROM {table_name};")
                            self.master.database_history.conn.commit()

                    except sqlite3.OperationalError as e:
                        messagebox.showerror(message=f"An error occurred when saving your database in memory: {e}",
                                             title='Error')
                    except Exception as e:
                        messagebox.showerror(message=f"An error occurred: {e}", title='Error')

                    self.master.database_preferences.close()
                    self.master.database_history.close()

                self.master.restart_app(open_preferences=True)
            elif os.path.expandvars(self.master.datastore_info.save_path) != os.path.expandvars(
                    self.preferences_save_location_var.get()):
                user_input = messagebox.askyesno(message="Do you want to keep your old settings?", title="File Removal")
                successful_path = self.master.datastore_info.set_save_path(self.preferences_save_location_var.get())
                successful_save_setting = self.master.datastore_info.set_save_settings(
                    self.preferences_save_settings_var.get())
                if not (successful_path or successful_save_setting):
                    messagebox.showwarning(message="We were unable to change some settings from the data paths. "
                                                   "Please check your computer if you have any registry keys in use.",
                                           title="Calculator Error")
                if hasattr(self.master.database_preferences, 'conn'):
                    self.master.database_preferences.apply(self.preferences_apply_btn)
                    self.master.database_preferences.close()
                if hasattr(self.master.database_history, 'conn'):
                    self.master.database_history.apply(self.history_apply_btn)
                    self.master.database_history.close()
                self.master.database_history.close() if hasattr(self.master.database_history, 'conn') else None
                self.master.database_preferences.close() if hasattr(self.master.database_preferences, 'conn') else None
                print(hasattr(self.master.database_history, 'conn'))
                shutil.copy2(self.master.database_history.database_file_name, os.path.join(
                    os.path.expandvars(self.preferences_save_location_var.get()), "history.db"))
                shutil.copy2(self.master.database_preferences.database_file_name, os.path.join(
                    os.path.expandvars(self.preferences_save_location_var.get()), "preferences.db"))
                if not user_input:
                    os.remove(self.master.database_history.database_file_name) if os.path.exists(
                        self.master.database_history.database_file_name) else None
                    os.remove(self.master.database_preferences.database_file_name) if os.path.exists(
                        self.master.database_preferences.database_file_name) else None
                    os.rmdir(self.master.database_preferences.database_folder) if not os.listdir(
                        self.master.database_preferences.database_folder) else None
                self.master.restart_app(open_preferences=True)
            else:
                successful_path = self.master.datastore_info.save_path
            
                successful_save_setting = self.master.datastore_info.set_save_settings(
                    self.preferences_save_settings_var.get())
                if not (successful_path or successful_save_setting):
                    messagebox.showwarning(message="We were unable to change some settings from the data paths. "
                                                   "Please check your computer if you have any registry keys in use.",
                                           title="Calculator Error")
                if hasattr(self.master.database_preferences, 'conn'):
                    self.master.database_preferences.apply(self.preferences_apply_btn)
                target_color = "0" if self.master.selected_mode == 'light' else "1" if (
                        self.master.selected_mode == 'dark') else "2"
                if self.master.database_preferences.get_preferences("darkmode")[0][2] != target_color:
                    self.master.restart_app(open_preferences=True) \
                        if ((not self.master.database_history.using_memory) or
                            (not self.master.database_preferences.using_memory)) \
                        else self.master.restart_app(
                        open_preferences=True,
                        darkmode=self.master.database_preferences.get_preferences("darkmode")[0][2],
                        storehistory=self.master.database_preferences.get_preferences("storehistory")[0][2])
        else:
            return
        
    def next_page(self):
        if self.history_current_page.get() == '':
            self.history_current_page.set('1')
            self.fetch_pages()
            return
        
        self.history_current_page.set(str(int(self.history_current_page.get()) + 1))
        self.fetch_pages()
        
    def prev_page(self):
        if self.history_current_page.get() == '':
            self.history_current_page.set('1')
            self.fetch_pages()
            return
        self.history_current_page.set(str(int(self.history_current_page.get()) - 1))
        self.fetch_pages()
        
    def validate_page_entry(self, p):
        if self.history_starter:
            self.history_starter = False
            return True
        
        if len(p) < 35 and (p.isdigit() or p == '') and (not p.startswith('0')):
            if p != '':
                if self.history_max_page >= int(p) >= 1:
                    self.after(20, self.fetch_pages)
                elif int(p) >= self.history_max_page:
                    self.after(10,
                               lambda: (self.history_current_page.set(str(self.history_max_page)),
                                        self.history_page.icursor('end')))
                    self.after(20, self.fetch_pages)
                    return False
                else:
                    return False
            return True
        return False
        
    def preferences_open_file_location(self):
        if file_path := filedialog.askdirectory(
                title="Select Data Location",
                initialdir=f"{os.getenv('LOCALAPPDATA') if os.getenv('LOCALAPPDATA') else ""}"):
            self.preferences_save_location_var.set(file_path.replace('/', '\\'))
            self.preferences_apply_btn.config(state='normal')
        
    def fetch_pages(self, switch=True):
        all_calculations = self.master.database_history.get_history_calculations()
        self.history_max_page = math.ceil(len(all_calculations) / 4) if len(all_calculations) > 0 else 1
        if switch:
            self.switch_tab('history')
        
        if int(self.history_current_page.get()) >= self.history_max_page:
            self.history_next_btn.config(state='disabled')
        else:
            self.history_next_btn.config(state='normal')
        
        if int(self.history_current_page.get()) <= 1:
            self.history_prev_btn.config(state='disabled')
        else:
            self.history_prev_btn.config(state='normal')
        
    def remove_frames(self):
        for i in sorted(self.history_selected_frames, key=lambda item: item.id, reverse=True):
            i.destroy()
            self.master.database_history.delete_from_history(i.id, self.history_clear_btn)
        self.history_selected_frames.clear()
        self.history_apply_btn.config(state=tk.NORMAL)
        
        if len(self.history_selected_frames) == 1:
            self.history_open_btn.config(state=tk.NORMAL)
        else:
            self.history_open_btn.config(state=tk.DISABLED)
            
        self.history_remove_btn.config(state=tk.DISABLED)
        self.switch_tab('history')
        self.history_items_selected.set(f"{len(self.history_selected_frames)} items selected")
    
    def open_history_frame(self):
        self.master.input_calculation.set(self.history_selected_frames[0].obj[1])
        self.master.input_display_content.set(self.history_selected_frames[0].obj[2])
        self.master.calc.set_variable_array_var(list(self.history_selected_frames[0].obj[3]))
        self.master.calc.update_scaling()
        self.close()
        
    # def update_selected_frames(self):
    # selected_frames_names_list = map(lambda f: str(f), self.history_selected_frames)
    # self.history_selected_frames.clear()
        
    # for index, name in enumerate(selected_frame_names_list):
    # widget = self.master.nametowidget(name)
    # widget.obj = self.history_selected_frames[index].obj
    # widget.id = self.history_selected_frames[index].id
    # self.history_selected_frames.append(widget)
        
    def select_frame(self, event, frame):
        if not event.state & 0x1:
            if frame not in self.history_selected_frames or len(self.history_selected_frames) > 1:
                for sel_frame in self.history_selected_frames:
                    try:
                        sel_frame.config(bg=self.history_old_calculations_inner['bg'])
                        sel_frame.operation_text.config(bg=self.history_old_calculations_inner['bg'])
                        sel_frame.result_text.config(bg=self.history_old_calculations_inner['bg'])
                        sel_frame.timestamp_text.config(bg=self.history_old_calculations_inner['bg'])
                    except tk.TclError:
                        continue
                    
                self.history_selected_frames.clear()
                # print("YES Shift - not inside frame")
                self.history_selected_frames.append(frame)
                frame.config(bg="#4A4A4A" if self.color != 'light' else '#C3C3C3')
                frame.operation_text.config(bg="#4A4A4A" if self.color != 'light' else '#C3C3C3')
                frame.result_text.config(bg="#4A4A4A" if self.color != 'light' else '#C3C3C3')
                frame.timestamp_text.config(bg="#4A4A4A" if self.color != 'light' else '#C3C3C3')
            else:
                for sel_frame in self.history_selected_frames:
                    try:
                        sel_frame.config(bg=self.history_old_calculations_inner['bg'])
                        sel_frame.operation_text.config(bg=self.history_old_calculations_inner['bg'])
                        sel_frame.result_text.config(bg=self.history_old_calculations_inner['bg'])
                        sel_frame.timestamp_text.config(bg=self.history_old_calculations_inner['bg'])
                    except tk.TclError:
                        continue
                    
                self.history_selected_frames.clear()
        else:
            if frame not in self.history_selected_frames:
                # print("NO Shift - not inside frame")
                self.history_selected_frames.append(frame)
                frame.config(bg="#4A4A4A" if self.color != 'light' else '#C3C3C3')
                frame.operation_text.config(bg="#4A4A4A" if self.color != 'light' else '#C3C3C3')
                frame.result_text.config(bg="#4A4A4A" if self.color != 'light' else '#C3C3C3')
                frame.timestamp_text.config(bg="#4A4A4A" if self.color != 'light' else '#C3C3C3')
            else:
                self.history_selected_frames.remove(frame) if frame in self.history_selected_frames else None
                frame.config(bg=self.history_old_calculations_inner['bg'])
                frame.operation_text.config(bg=self.history_old_calculations_inner['bg'])
                frame.result_text.config(bg=self.history_old_calculations_inner['bg'])
                frame.timestamp_text.config(bg=self.history_old_calculations_inner['bg'])
        if len(self.history_selected_frames) == 1:
            self.history_open_btn.config(state=tk.NORMAL)
            self.history_remove_btn.config(state=tk.NORMAL)
        else:
            self.history_open_btn.config(state=tk.DISABLED)
            self.history_remove_btn.config(state=tk.NORMAL if len(self.history_selected_frames) != 0 else tk.DISABLED)
            
        self.history_items_selected.set(f"{len(self.history_selected_frames)} items selected")
            
    def set_as_selected_frame(self, frame):
        for i, string in enumerate(map(lambda f: str(f), self.history_selected_frames)):
            if string == str(frame):
                self.history_selected_frames[i] = frame
        frame.config(bg="#4A4A4A" if self.color != 'light' else '#C3C3C3')
        frame.operation_text.config(bg="#4A4A4A" if self.color != 'light' else '#C3C3C3')
        frame.result_text.config(bg="#4A4A4A" if self.color != 'light' else '#C3C3C3')
        frame.timestamp_text.config(bg="#4A4A4A" if self.color != 'light' else '#C3C3C3')
    
    def clean_history(self):
        for frame in self.history_old_calculations:
            frame.destroy()
        self.history_old_calculations.clear()
    
    def show_history(self):
        self.history_no_history_msg.place_forget()
        self.history_no_history_ok_btn.place_forget()
        self.history_name.place(x=20, y=10)
        self.history_selected_items.place(x=-20, y=10, relx=1.0, anchor='ne')
        self.history_old_calculations_frame.place(x=20, y=35, relwidth=1.0, width=-44)
        self.history_old_calculations_inner.place(relwidth=1.0, relheight=1.0)
        self.history_prev_btn.place(x=20, y=145)
        self.history_page.place(x=41, y=145, height=22)
        self.history_next_btn.place(x=66, y=145)
        self.history_clear_btn.place(x=87, y=145)
        self.history_open_btn.place(x=139, y=145)
        self.history_remove_btn.place(x=191, y=145)
        self.history_apply_btn.place(x=256, y=145)
        self.history_page.config(validate='key', validatecommand=(self.history_page_validation, '%P'))
    
    def show_no_history_msg(self):
        self.history_name.place_forget()
        self.history_selected_items.place_forget()
        self.history_old_calculations_frame.place_forget()
        self.history_old_calculations_inner.place_forget()
        self.history_prev_btn.place_forget()
        self.history_page.place_forget()
        self.history_next_btn.place_forget()
        self.history_clear_btn.place_forget()
        self.history_open_btn.place_forget()
        self.history_remove_btn.place_forget()
        self.history_apply_btn.place_forget()
        self.history_no_history_ok_btn.place(x=-45, y=-45, anchor='se', relx=1.0, rely=1.0)
        self.history_no_history_msg.place(relx=0.5, anchor='n', y=45)
    
    def add_history(self, obj):
        self.history_old_calculations.append(tk.Frame(self.history_old_calculations_inner,
                                                      bg=self.history_old_calculations_inner['bg'], height=10,
                                                      name=f"calculationin{obj[0]}"))
        self.history_old_calculations[-1].id = obj[0]
        self.history_old_calculations[-1].obj = obj
        self.history_old_calculations[-1].frame_name = f"calculationin{obj[0]}"
        self.history_old_calculations[-1].remove = tk.Button(
            self.history_old_calculations[-1], text='-', bg='#FF0000', fg='white', bd=0, padx=5,
            font=("Calibri", 9), highlightthickness=0, relief=tk.SUNKEN,
            command=lambda id_=obj[0], frame=self.history_old_calculations[-1]: (
                self.master.database_history.delete_from_history(id_, self.history_clear_btn),
                frame.destroy(), self.history_apply_btn.config(state=tk.NORMAL),
                self.history_selected_frames.remove(frame) if frame in self.history_selected_frames else None,
                self.history_items_selected.set(f"{len(self.history_selected_frames)} items selected"),
                (self.history_open_btn.config(state=tk.NORMAL),
                 self.history_remove_btn.config(state=tk.NORMAL)) if len(self.history_selected_frames) == 1 else (
                    self.history_open_btn.config(state=tk.DISABLED),
                    self.history_remove_btn.config(
                        state=tk.NORMAL if len(self.history_selected_frames) != 0 else tk.DISABLED))))
        self.history_old_calculations[-1].remove.pack(side='left', padx=5)
        self.history_old_calculations[-1].operation_text = tk.Label(
            self.history_old_calculations[-1], text=obj[2][:11].rstrip() if len(obj[2].rstrip()) <= 11
            else obj[2][:11].rstrip()+'...', bg=self.history_old_calculations_inner['bg'],
            fg='white' if self.color != 'light' else 'black', font=("Calibri", 9))
        self.history_old_calculations[-1].operation_text.pack(side='left')
        self.history_old_calculations[-1].result_text = tk.Label(
            self.history_old_calculations[-1], text="= "+(obj[5][:7] if len(obj[5]) <= 7 else obj[5][:7]+'...'),
            bg=self.history_old_calculations_inner['bg'], fg='white' if self.color != 'light' else 'black',
            font=("Calibri", 9))
        self.history_old_calculations[-1].result_text.pack(side='left')
        self.history_old_calculations[-1].timestamp_text = tk.Label(self.history_old_calculations[-1],
                                                                    text="|  " + obj[7],
                                                                    bg=self.history_old_calculations_inner['bg'],
                                                                    fg='white' if self.color != 'light' else 'black',
                                                                    font=("Calibri", 9))
        self.history_old_calculations[-1].timestamp_text.pack(side='right', padx=(0, 10))
        self.history_old_calculations[-1].pack(fill='x', pady=(5, 0))
        
        self.history_old_calculations[-1].bind(
            "<ButtonPress-1>", lambda event, frame=self.history_old_calculations[-1]: self.select_frame(event, frame))
        self.history_old_calculations[-1].operation_text.bind(
            "<ButtonPress-1>", lambda event, frame=self.history_old_calculations[-1]: self.select_frame(event, frame))
        self.history_old_calculations[-1].result_text.bind(
            "<ButtonPress-1>", lambda event, frame=self.history_old_calculations[-1]: self.select_frame(event, frame))
        self.history_old_calculations[-1].timestamp_text.bind(
            "<ButtonPress-1>", lambda event, frame=self.history_old_calculations[-1]: self.select_frame(event, frame))
        
        if str(self.history_old_calculations[-1]) in map(lambda f: str(f), self.history_selected_frames):
            self.set_as_selected_frame(self.history_old_calculations[-1])
    
    def close(self):
        if self.history_apply_btn['state'] == 'normal':
            self.master.database_history.conn.rollback()
        if self.preferences_apply_btn['state'] == 'normal':
            self.master.database_preferences.conn.rollback()
        
        self.master.settings_open = False
        self.master.settings_instance = None
        self.destroy()
        
    def get_tab(self):
        return self.open_tab
        
    def switch_tab(self, tab):
        if tab == 'preferences':
            self.tab_preferences.config(bg="#2A2A2A" if self.color != 'light' else '#E6E6E6')
            self.tab_history.config(bg="#171717" if self.color != 'light' else '#D3D3D3')
            self.tab_about.config(bg="#171717" if self.color != 'light' else '#D3D3D3')
            
            self.preferences_frame.pack_forget()
            self.preferences_frame.pack(expand=True, fill='both')
            self.history_frame.pack_forget()
            self.about_frame.pack_forget()
            
            self.open_tab = 'preferences'
        elif tab == 'history':
            self.tab_preferences.config(bg="#171717" if self.color != 'light' else '#D3D3D3')
            self.tab_history.config(bg="#2A2A2A" if self.color != 'light' else '#E6E6E6')
            self.tab_about.config(bg="#171717" if self.color != 'light' else '#D3D3D3')
            
            self.history_frame.pack_forget()
            self.preferences_frame.pack_forget()
            self.clean_history()
            if self.master.database_preferences.get_preferences('storehistory')[0][2] == '1':
                self.show_history()
                for i in list(reversed(self.master.database_history.get_history_calculations()))[
                         (int(self.history_current_page.get())-1)*4:int(self.history_current_page.get())*4]:
                    self.add_history(i)
                self.fetch_pages(switch=False)
            else:
                self.show_no_history_msg()
                
            self.history_frame.pack(expand=True, fill='both')
            self.about_frame.pack_forget()
            
            self.open_tab = 'history'
        elif tab == 'about':
            self.tab_preferences.config(bg="#171717" if self.color != 'light' else '#D3D3D3')
            self.tab_history.config(bg="#171717" if self.color != 'light' else '#D3D3D3')
            self.tab_about.config(bg="#2A2A2A" if self.color != 'light' else '#E6E6E6')
            
            self.about_frame.pack_forget()
            self.preferences_frame.pack_forget()
            self.history_frame.pack_forget()
            self.about_frame.pack(expand=True, fill='both')
            
            self.open_tab = 'about'
    
    
    
    