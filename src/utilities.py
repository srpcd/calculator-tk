import tkinter as tk
import ctypes as ct
import time
from tkinter import ttk
from abc import ABC, abstractmethod

DWM_WA_USE_IMMERSIVE_DARK_MODE = 20
DWM_WA_USE_IMMERSIVE_DARK_MODE_BEFORE_20H1 = 19


class WindowsTitlebar(ABC):
    def __init__(self):
        self.window = None

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def winfo_id(self):
        pass

    def _dark_title_bar(self):
        """
        MORE INFO:
        https://learn.microsoft.com/en-us/windows/win32/api/dwmapi/ne-dwmapi-dwmwindowattribute
        """
        self.update()
        set_window_attribute = ct.windll.dwmapi.DwmSetWindowAttribute
        get_parent = ct.windll.user32.GetParent
        hwnd = get_parent(self.winfo_id())
        value = ct.c_int(1)
        if set_window_attribute(hwnd, DWM_WA_USE_IMMERSIVE_DARK_MODE, ct.byref(value),
                                ct.sizeof(value)) != 0:
            set_window_attribute(hwnd, DWM_WA_USE_IMMERSIVE_DARK_MODE_BEFORE_20H1,
                                 ct.byref(value), ct.sizeof(value))

    def _light_title_bar(self):
        """
        MORE INFO:
        https://learn.microsoft.com/en-us/windows/win32/api/dwmapi/ne-dwmapi-dwmwindowattribute
        """
        self.update()
        set_window_attribute = ct.windll.dwmapi.DwmSetWindowAttribute
        get_parent = ct.windll.user32.GetParent
        hwnd = get_parent(self.winfo_id())
        value = ct.c_int(0)
        if set_window_attribute(hwnd, DWM_WA_USE_IMMERSIVE_DARK_MODE, ct.byref(value),
                                ct.sizeof(value)) != 0:
            set_window_attribute(hwnd, DWM_WA_USE_IMMERSIVE_DARK_MODE_BEFORE_20H1,
                                 ct.byref(value), ct.sizeof(value))


def left_chars_strip(s: str, ch: str):
    count = 0
    for i, char in enumerate(s):
        if char == ch:
            count += 1
        else:
            break
    return count, s.lstrip(ch)


def wait_for_file(file_path, timeout=30, interval=0.5):
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with open(file_path, 'a'):
                return True
        except PermissionError:
            pass
        time.sleep(interval)
    return False


class ThemedMenu(tk.Toplevel):
    """
    Better than the old bad menu that has an annoying border
    """
    
    def __init__(self, master=None, **kw) -> None:
        self.using_parent_master = kw.pop('using_parent_master', False)
        self.master_class = kw.pop('master_menu', None)
        self.label_name = kw.pop('label_name', "ThemedMenu")
        self.main_cascade_button = kw.pop('main_cascade_button', None)  # this must be from a themed menu bar
        
        super().__init__(master)
        
        self._toplevel_entered_state = False
        self._width = kw.pop('windowWidth', 112)
        self._height = kw.pop('windowHeight', 180)
        
        self.title("Menu")
        self.config(**kw)
        self.overrideredirect(True)
        self.withdraw()
        self.is_open = False
        
        self.main_frame = tk.Frame(self, bg=self['bg'], bd=0, highlightthickness=0, relief=tk.SUNKEN)
        self.main_frame.pack(expand=True, fill='both')
        
        self.objects: list = []
        
    def add_command(self, label: str = None, command=None, **kw) -> None:
        hoverbackground = kw.pop('hoverbackground', None)
        
        if command is None:
            self.objects.append(tk.Button(self.main_frame, text=label, command=self.close, anchor='w', **kw))
        else:
            self.objects.append(tk.Button(self.main_frame, text=label, command=lambda: (command(), self.close()),
                                          anchor='w', **kw))
        self.objects[-1].grid(row=len(self.objects), column=0, sticky='news')
        
        if kw.get('bg', kw.get('background')) and hoverbackground:
            self.objects[-1].bind("<Enter>", lambda event, button=self.objects[-1]: button.config(bg=hoverbackground))
            self.objects[-1].bind("<Leave>", lambda event, button=self.objects[-1]: button.config(bg=kw.get(
                'bg', kw.get('background', None))))

        return self.objects[-1]
        
    def pre_close_action(self, button, kw, toplevel):
        if self._toplevel_entered_state:
            return
        if toplevel.using_parent_master:
            self.bind("<FocusOut>", lambda event: self.close())

        button.config(bg=kw.get('bg', kw.get('background', None)))
        toplevel.close()
        
    def set_toplevel_entered_state(self, state: bool, button=None, kw=None, toplevel=None):
        if not state:
            self.pre_close_action(button, kw, toplevel)
        
        self._toplevel_entered_state = state
        
    def add_cascade(self, label: str = None, toplevel=None, **kw) -> None:
        hoverbackground = kw.pop('hoverbackground', None)
        x_offset = kw.pop('x_offset', 0)
        y_offset = kw.pop('y_offset', 0)
        
        self.objects.append(tk.Button(self.main_frame, text=label, anchor='w', **kw))
        self.objects[-1].grid(row=len(self.objects), column=0, sticky='news')
            
        if kw.get('bg', kw.get('background')) and hoverbackground:
            self.objects[-1].bind("<Enter>", lambda event, button=self.objects[-1]: (
                button.config(bg=hoverbackground),
                self.main_frame.after(
                    10, lambda: toplevel.post(
                        self.winfo_rootx()+self._width+x_offset,
                        self.winfo_rooty()+len(self.objects)*11+2+y_offset))))
            toplevel.bind("<Enter>", lambda event: self.set_toplevel_entered_state(True))
            toplevel.bind("<Leave>", lambda event, button=self.objects[-1]: self.set_toplevel_entered_state(
                False, button, kw, toplevel))
            self.objects[-1].bind("<Leave>", lambda event, button=self.objects[-1]: self.main_frame.after(
                10, lambda: self.pre_close_action(button, kw, toplevel)))

        return self.objects[-1]
        
    def add_separator(self):
        self.objects.append(ttk.Separator(self.main_frame, orient='horizontal',
                                          style="MenuSeparator.Horizontal.TSeparator"))
        self.objects[-1].grid(row=len(self.objects), column=0, sticky='ew')

        return self.objects[-1]
        
    def close(self):
        self.withdraw()
        self.unbind("<FocusOut>")
        self.is_open = False
        if self.main_cascade_button:
            self.main_cascade_button.config(bg=self.main_cascade_button.config(
                bg=self.main_cascade_button.kw.get('bg', self.main_cascade_button.kw.get('background', None))))
            self.main_cascade_button.bind("<Enter>", lambda event: (self.main_cascade_button.config(
                bg=self.main_cascade_button.hoverbackground), self.main_cascade_button.parent.activate_by_hover(event)))
            self.main_cascade_button.bind("<Leave>", lambda event: self.main_cascade_button.config(
                bg=self.main_cascade_button.kw.get('bg', self.main_cascade_button.kw.get('background', None))))
    
    def post(self, x, y):
        self.geometry("{}x{}+{}+{}".format(self._width, self._height, x, y))
        self.deiconify()
        self.is_open = True
        
        if self.main_cascade_button:
            self.main_cascade_button.config(bg=self.main_cascade_button.hoverbackground)
            self.main_cascade_button.unbind("<Enter>")
            self.main_cascade_button.unbind("<Leave>")
        
        if self.using_parent_master:
            self.master_class.unbind("<FocusOut>")
        else:
            self.focus_force()
            self.bind("<FocusOut>", lambda event: self.close())


class ThemedMenubar(tk.Frame):
    def __init__(self, master=None, **kw) -> None:
        if 'arrow_syntax' in kw.keys():
            self.arrow_syntax = True
            kw.pop('arrow_syntax')
        else:
            self.arrow_syntax = False
    
        super().__init__(master, **kw)
        self.master = master
        self.cur_menubutton = None
        self.widget = None
        self.buttons: list = []
        self.menus: list = []

    def shift_left_menu(self, event):
        self.widget = event.widget
        self.widget.config(bg=self.widget['activebackground'])
    
    def shift_right_menu(self):
        for menubutton in self.buttons:
            menubutton.config(bg=self['background'])
    
    def activate_by_hover(self, event):
        opened_menu = None
        i = None
        for i in self.buttons:
            if i.ctoplevel.is_open:
                opened_menu = i
                break
        if opened_menu is None:
            return
        if event.widget is not i:
            opened_menu.ctoplevel.close()
            event.widget.invoke()

    # def add_cascade(self, label: str = None, menu=None, **kw):
        # if not menu:
            # self.buttons.append(tk.Menubutton(self, text=label, **kw))
        # else:
            # self.buttons.append(tk.Menubutton(self, text=label, menu=menu, **kw))
            # self.buttons[-1].cmenu = menu

        # return self.buttons[-1]
        
    def add_cascade_toplevel(self, label: str = None, toplevel=None, **kw):
        hoverbackground = kw.pop('hoverbackground', None)
        x_offset = kw.pop('x_offset', 0)
        y_offset = kw.pop('y_offset', 0)
        
        if not toplevel:
            self.buttons.append(tk.Button(self, text=label, **kw))
        else:
            self.buttons.append(tk.Button(self, text=label, command=lambda: toplevel.post(
                self.winfo_rootx()+x_offset, self.winfo_rooty()+20+y_offset), **kw))
            self.buttons[-1].ctoplevel = toplevel
        
        self.buttons[-1].parent = self
        self.buttons[-1].kw = kw
        self.buttons[-1].hoverbackground = hoverbackground
            
        if kw.get('bg', kw.get('background')) and hoverbackground:
            self.buttons[-1].bind("<Enter>", lambda event, button=self.buttons[-1]: (button.config(bg=hoverbackground),
                                                                                     self.activate_by_hover(event)))
            self.buttons[-1].bind("<Leave>", lambda event, button=self.buttons[-1]: button.config(
                bg=kw.get('bg', kw.get('background', None))))
        else:
            self.buttons[-1].bind("<Enter>", lambda event: self.activate_by_hover(event))

        return self.buttons[-1]

    def menu_bind_all(self):
        for index, menubutton in enumerate(self.buttons):
            menubutton.bind("<ButtonPress-1>", self.shift_left_menu)
            self.master.bind("<ButtonPress-1>", lambda event: self.shift_right_menu())

    # def edit_cascade(self, index: int, **kw) -> None:
        # self.buttons[index].config(**kw)
        # if 'menu' in kw.keys():
            # self.buttons[index].cmenu = kw['menu']
            
    def edit_cascade_toplevel(self, index: int, **kw) -> None:
        self.buttons[index].config(**kw)
        if 'toplevel' in kw.keys():
            self.buttons[index].ctoplevel = kw['toplevel']
            
            