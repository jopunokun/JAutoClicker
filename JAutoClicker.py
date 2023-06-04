import time
import threading
import tkinter as tk
from tkinter import ttk, Text
from tkinter import *
from pynput import keyboard
from pynput.mouse import Button
from pynput.mouse import Controller as mouse_controller
from pynput.keyboard import Key, Listener
from pynput.keyboard import Controller as keyboard_controller
class AutoClicker:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("JAutoClicker")
        self.root.geometry("550x390")
        self.root.iconbitmap("assets/mouse.ico")
        self.root.resizable(False, False)
        self.root.configure(background='#292929')
        self.root.attributes('-topmost', True)
        self.is_running = False
        self.is_toggled = False
        self.is_binding_key = False
        self.button_press = False
        self.choose_pos_var = False
        self.click_thread = None
        self.cps = 20
        self.pos = (0, 0)
        self.keyboard_button = 'a'
        self.keybind = Key.f8
        self.button = Button.left
        self.mouse = mouse_controller()
        self.keyboard = keyboard_controller()

        # set dropdown style
        style = ttk.Style()
        style.theme_use("xpnative")


        # CPS frame
        self.cps_frame = tk.Frame(self.root, padx=10, pady=10, bg='#292929')
        cps_label = tk.Label(self.cps_frame, text="CPS (Click per Second)", bg='#292929', fg='white', font=('Arial', 12))
        cps_label.pack(side=tk.LEFT, anchor='w')
        self.cps_var = tk.StringVar()
        self.cps_var.set(str(self.cps))
        self.cps_var.trace("w", self.cps_check)
        self.cps_input = tk.Entry(self.cps_frame, textvariable=self.cps_var, bd=1, relief='groove', font=('Arial', 12))
        self.cps_input.place(width=34, height=30)
        self.cps_input.pack(side=tk.LEFT, anchor='w')
        self.cps_input.config(validate="key")
        self.cps_input.config(validatecommand=(self.cps_input.register(self.validate_numeric_input), '%P'))
        self.cps_frame.pack(anchor='w')


        # click device frame
        self.click_device_frame = tk.Frame(self.root, padx=10, pady=2, bg='#292929')
        click_device_lbl = tk.Label(self.click_device_frame, text='Click device', bg='#292929', fg='white', font=('Arial', 12))
        click_device_lbl.pack(side=tk.LEFT, anchor='w')
        self.device_var = tk.StringVar()
        self.device_var.set("Mouse")
        self.click_device_options = ["Mouse", "Keyboard"]

        click_device_dropdown = ttk.Combobox(self.click_device_frame, textvariable=self.device_var, values=self.click_device_options, state="readonly", width=20)
        click_device_dropdown.pack(side=tk.LEFT, anchor='w')
        click_device_dropdown.bind('<<ComboboxSelected>>', lambda e: (self.click_device_frame.focus(), self.change_device()))
        self.click_device_frame.pack(anchor='w')


        # CLICK OPTION TITLE (COL 1)
        self.title_frame = tk.Frame(self.root, padx=10, bg='#292929')
        click_option_title = tk.Label(self.title_frame, text='Click Options', bg='#292929', fg='white', font=('Arial', 8))
        click_option_title.pack(side=tk.LEFT, anchor='w')
        # KEYBIND OPTIONS TITLE (COL 2)
        keybind_option_title = tk.Label(self.title_frame, text='Keybind Options', bg='#292929', fg='white', font=('Arial', 8))
        keybind_option_title.pack(side=tk.RIGHT, anchor='e', padx=(206, 0))
        self.title_frame.pack(anchor='w', pady=(20, 4))


        # ROW 1
        # Click Button frame (ROW 1 COL 1)
        self.row_1_frame = tk.Frame(self.root, bg='#292929', padx=10)
        click_button_label = tk.Label(self.row_1_frame, text="Mouse Button", bg='#292929', fg='white', font=('Arial', 12))
        click_button_label.pack(side=tk.LEFT, anchor='w')
        self.button_var = tk.StringVar()
        self.button_var.set("Left")
        click_button_options = ["Left", "Right", "Middle"]
        click_device_dropdown = ttk.Combobox(self.row_1_frame, textvariable=self.button_var, values=click_button_options, state="readonly", width=21)
        click_device_dropdown.pack(side=tk.LEFT, anchor='w')
        click_device_dropdown.bind('<<ComboboxSelected>>', lambda e: (self.row_1_frame.focus()))

        # Keybind frame (ROW 1 COL 2)
        keybind_label = tk.Label(self.row_1_frame, text="Keybind", font=('Arial', 12), fg='white', bg='#292929')
        keybind_label.pack(side=tk.LEFT, anchor='e', padx=(21, 0))
        self.keybind_input = tk.Label(self.row_1_frame, text='F8', bd=1, width=25, font=('Arial', 12), fg='white', bg='#292929', anchor='w')
        self.keybind_input.pack(side=tk.LEFT, padx=(5, 0))
        self.row_1_frame.pack(anchor='w')


        # ROW 2
        # Click Type Frame (ROW 2 COL 1)
        self.row_2_frame = tk.Frame(self.root, bg='#292929', padx=10, pady=10)
        click_type_lbl = tk.Label(self.row_2_frame, text='Click Type', bg='#292929', fg='white', font=('Arial', 12))
        click_type_lbl.pack(side=tk.LEFT, anchor='w')
        self.click_type_var = tk.StringVar()
        self.click_type_var.set("Single Click")
        click_type_options = ["Single Click", "Double Click", "Triple Click"]
        self.click_type_dropdown = ttk.Combobox(self.row_2_frame, textvariable=self.click_type_var, values=click_type_options, state="readonly", width=25)
        self.click_type_dropdown.pack(side=tk.LEFT, anchor='w')
        self.click_type_dropdown.bind("<<ComboboxSelected>>", lambda e: self.row_2_frame.focus())

        # Keybind Button Frame (ROW 2 COL 2)
        self.change_keybind_button = tk.Button(self.row_2_frame, text="Change Keybind", width=12, command=self.on_change_keybind_button_click)
        self.change_keybind_button.pack(side=tk.LEFT, anchor='e', padx=(21, 3))
        self.reset_keybind_button = tk.Button(self.row_2_frame, text='Reset Keybind', width=12, command=self.reset_keybind)
        self.reset_keybind_button.pack(side=tk.LEFT, anchor='e')
        self.row_2_frame.pack(anchor='w')


        # ROW 3
        # Click Pos Frame (ROW 3 COl 1)
        self.row_3_frame = tk.Frame(self.root, padx=10, bg='#292929')
        click_pos_lbl = tk.Label(self.row_3_frame, text='Click Position', bg='#292929', fg='white', font=('Arial', 12))
        click_pos_lbl.pack(side=tk.LEFT, anchor='w')
        self.pos_var = tk.StringVar()
        self.pos_var.set('Current Cursor Position')
        click_pos_options = ['Current Cursor Position', 'Pick Location']
        click_device_dropdown = ttk.Combobox(self.row_3_frame, textvariable=self.pos_var, values=click_pos_options, state="readonly", width=21)
        click_device_dropdown.pack(side=tk.LEFT, anchor='w')
        click_device_dropdown.bind('<<ComboboxSelected>>', lambda e: (self.row_3_frame.focus(), self.change_pos()))
        self.row_3_frame.pack(anchor='w')


        # ROW 4
        # Set Click Pos (ROW 4 COL 1)
        self.row_4_frame = tk.Frame(self.root, bg='#292929')
        choose_click_pos_btn = tk.Button(self.row_4_frame, text="Choose Click Position", command=lambda: self.choose_pos())
        choose_click_pos_btn.pack(side=tk.LEFT, anchor='w')


        # ROW 7
        # Click Pos x y
        self.row_7_frame = tk.Frame(self.root, bg='#292929')
        self.click_pos_lbl = tk.Label(self.row_7_frame, bg='#292929', fg='white', text="x = 0, y = 0", font=('Arial', 12))
        self.click_pos_lbl.pack(side=tk.LEFT, anchor='w')


        # ROW 5
        # Start Stop Button (ROW 5 COL 1,2)
        self.row_5_frame = tk.Frame(self.root, bg='#292929')
        self.start_button = tk.Button(self.row_5_frame, text='Start', width=15, height=3, command=self.start_clicker, font=('Arial', 10))
        self.start_button.pack(side=LEFT, padx=5)
        self.stop_button = tk.Button(self.row_5_frame, text='Stop', width=15, height=3, command=self.stop_clicker, font=('Arial', 10))
        self.stop_button.pack(side=RIGHT, padx=5)
        self.row_5_frame.pack(pady=(40, 0))

        # PRESS OPTION TITLE (COL 1)
        self.keyboard_title_frame = tk.Frame(self.root, padx=10, bg='#292929')
        keyboard_click_option_title = tk.Label(self.keyboard_title_frame, text='Press Options', bg='#292929', fg='white', font=('Arial', 8))
        keyboard_click_option_title.pack(side=tk.LEFT, anchor='w')
        # KEYBIND OPTIONS TITLE (COL 2)
        keyboard_keybind_option_title = tk.Label(self.keyboard_title_frame, text='Keybind Options', bg='#292929', fg='white', font=('Arial', 8))
        keyboard_keybind_option_title.pack(side=tk.RIGHT, anchor='e', padx=(200, 0))


        # Keyboard ROW 1
        # Click Button frame (ROW 1 COL 1)
        self.keyboard_row_1_frame = tk.Frame(self.root, bg='#292929', padx=10)
        keyboard_click_button_label = tk.Label(self.keyboard_row_1_frame, text="Keyboard Key", bg='#292929', fg='white', font=('Arial', 12))
        keyboard_click_button_label.pack(side=tk.LEFT, anchor='w')
        self.keyboard_key_lbl = tk.Label(self.keyboard_row_1_frame, text='A', font=('Arial', 12), width=14)
        self.keyboard_key_lbl.pack(side=tk.LEFT, anchor='w')

        # Keybind frame (ROW 1 COL 2)
        keyboard_keybind_label = tk.Label(self.keyboard_row_1_frame, text="Keybind", font=('Arial', 12), fg='white', bg='#292929')
        keyboard_keybind_label.pack(side=tk.LEFT, anchor='e', padx=(36, 0))
        self.keyboard_keybind_input = tk.Label(self.keyboard_row_1_frame, text='F8', bd=1, width=25, font=('Arial', 12), fg='white', bg='#292929', anchor='w')
        self.keyboard_keybind_input.pack(side=tk.LEFT, padx=(5, 0))


        # Keyboard ROW 2
        # Press Type Frame (ROW 2 COL 1)
        self.keyboard_row_2_frame = tk.Frame(self.root, bg='#292929', padx=10, pady=10)
        click_type_lbl = tk.Label(self.keyboard_row_2_frame, text='Press Type', bg='#292929', fg='white', font=('Arial', 12))
        click_type_lbl.pack(side=tk.LEFT, anchor='w')
        self.press_type_var = tk.StringVar()
        self.press_type_var.set("Single Press")
        press_type_options = ["Single Press", "Double Press", "Triple Press"]
        self.click_type_dropdown = ttk.Combobox(self.keyboard_row_2_frame, textvariable=self.press_type_var, values=press_type_options, state="readonly", width=21)
        self.click_type_dropdown.pack(side=tk.LEFT, anchor='w')
        self.click_type_dropdown.bind("<<ComboboxSelected>>", lambda e: self.keyboard_row_2_frame.focus())

        # Keybind Button Frame (ROW 2 COL 2)
        self.change_keybind_button = tk.Button(self.keyboard_row_2_frame, text="Change Keybind", width=12, command=self.on_change_keybind_button_click)
        self.change_keybind_button.pack(side=tk.LEFT, anchor='e', padx=(40, 3))
        self.reset_keybind_button = tk.Button(self.keyboard_row_2_frame, text='Reset Keybind', width=12, command=self.reset_keybind)
        self.reset_keybind_button.pack(side=tk.LEFT, anchor='e')


        # Keyboard ROW 3
        self.keyboard_row_3_frame = tk.Frame(self.root, padx=50, bg='#292929')
        keyboard_press_change_btn = tk.Button(self.keyboard_row_3_frame, padx=20, pady=3, text="Change Key to Press", command=self.change_button_press)
        keyboard_press_change_btn.pack(side=tk.LEFT)

        # Warning msg
        self.row_6_frame = tk.Frame(self.root, bg='#292929')
        title_lbl = tk.Label(self.row_6_frame, text='Warning:', fg='red', bg='#292929', font=('Arial', 9))
        title_lbl.pack(pady=(10, 0))
        self.warning_msg = tk.Label(self.row_6_frame, text='WARNING TEXT', fg='red', bg='#292929', font=('Arial', 9))
        self.warning_msg.pack()

        self.listener = Listener(on_press=self.on_key_press)
        self.listener.start()

    def validate_numeric_input(self, text):
        if text.isdigit():
            return True
        else:
            return False

    def cps_check(self, *args):
        if int(self.cps_var.get()) > 200:
            self.cps_var.set('200')
            self.warning_msg.config(text='CPS cannot be higher than 200')
            self.row_6_frame.pack(pady=(10, 0))
        else:
            self.row_6_frame.pack_forget()

    def reset_keybind(self):
        if str(Key.f8) != str(self.keyboard_button) and self.device_var.get() == 'Keyboard':
            self.is_binding_key = False
            self.keybind = Key.f8
            if isinstance(Key.f8, keyboard.Key):
                self.keybind_input.config(text=Key.f8.name.capitalize(), fg='white')
                self.keyboard_keybind_input.config(text=Key.f8.name.capitalize(), fg='white')
                self.row_6_frame.pack_forget()
            else:
                self.keybind_input.config(text=Key.f8.char.capitalize() if hasattr(Key.f8, 'char') else Key.f8.name.capitalize(), fg='white')
                self.keyboard_keybind_input.config(text=Key.f8.char.capitalize() if hasattr(Key.f8, 'char') else Key.f8.name.capitalize(), fg='white')
                self.row_6_frame.pack_forget()
        elif self.device_var.get() == 'Mouse':
            self.is_binding_key = False
            self.keybind = Key.f8
            if isinstance(Key.f8, keyboard.Key):
                self.keybind_input.config(text=Key.f8.name.capitalize(), fg='white')
                self.keyboard_keybind_input.config(text=Key.f8.name.capitalize(), fg='white')
                self.row_6_frame.pack_forget()
            else:
                self.keybind_input.config(text=Key.f8.char.capitalize() if hasattr(Key.f8, 'char') else Key.f8.name.capitalize(), fg='white')
                self.keyboard_keybind_input.config(text=Key.f8.char.capitalize() if hasattr(Key.f8, 'char') else Key.f8.name.capitalize(), fg='white')
                self.row_6_frame.pack_forget()
        else:
            self.is_binding_key = False
            self.warning_msg.config(text='Key CANNOT be the same as key to press', fg='red')
            self.row_6_frame.pack()

    def on_change_keybind_button_click(self):
        self.keybind_old = self.keybind_input.cget('text')
        self.is_binding_key = True
        self.keybind_input.config(text='Press any key to set keybind\nESC to cancel', fg='green')
        self.keyboard_keybind_input.config(text='Press any key to set keybind\nESC to cancel', fg='green')

    def change_button_press(self):
        self.click_keyboard_old = self.keyboard_key_lbl.cget('text')
        self.keyboard_key_lbl.config(text='Press any key\nESC to cancel', fg='green')
        self.button_press = True

    def choose_pos(self):
        self.click_pos_old = self.click_pos_lbl.cget('text')
        self.click_pos_lbl.config(text='Move your mouse and press\nENTER to confirm position\nESC to cancel', fg='green')
        self.listener2 = Listener(on_press=self.assign_pos)
        self.listener2.start()
        self.choose_pos_var = True

    def assign_pos(self, key):
        if key == Key.enter:
            self.pos = self.mouse.position
            self.click_pos_lbl.config(text='x = {}, y = {}'.format(self.pos[0], self.pos[1]), fg='white')
            self.listener2.stop()

    def change_pos(self, event=None):
        if self.pos_var.get() == 'Current Cursor Position':
            self.row_4_frame.pack_forget()
            self.row_6_frame.pack_forget()
            self.row_7_frame.pack_forget()
            self.root.geometry("550x390")
        else:
            self.row_5_frame.pack_forget()
            self.row_4_frame.pack(anchor='w', padx=(80, 0), pady=(10, 0))
            self.row_7_frame.pack(anchor='w', padx=(80, 0))
            self.row_5_frame.pack(pady=(40, 0))
            self.row_6_frame.pack_forget()
            self.root.geometry("550x450")

    def change_device(self, event=None):
        if self.device_var.get() == 'Mouse':
            self.keyboard_title_frame.pack_forget()
            self.keyboard_row_1_frame.pack_forget()
            self.keyboard_row_2_frame.pack_forget()
            self.keyboard_row_3_frame.pack_forget()
            self.row_5_frame.pack_forget()
            self.row_6_frame.pack_forget()

            self.title_frame.pack(anchor='w', pady=(20, 4))
            self.row_1_frame.pack(anchor='w')
            self.row_2_frame.pack(anchor='w')
            self.row_3_frame.pack(anchor='w')
            self.click_pos_lbl.pack(side=tk.LEFT, anchor='w')
            self.change_pos()
            self.row_5_frame.pack(pady=(40, 0))
            self.row_6_frame.pack_forget()
        elif self.device_var.get() == 'Keyboard':
            self.title_frame.pack_forget()
            self.row_1_frame.pack_forget()
            self.row_2_frame.pack_forget()
            self.row_3_frame.pack_forget()
            self.row_4_frame.pack_forget()
            self.click_pos_lbl.pack_forget()
            self.row_5_frame.pack_forget()
            self.row_6_frame.pack_forget()
            self.row_7_frame.pack_forget()

            self.keyboard_title_frame.pack(anchor='w', pady=(20, 4))
            self.keyboard_row_1_frame.pack(anchor='w')
            self.keyboard_row_2_frame.pack(anchor='w')
            self.keyboard_row_3_frame.pack(anchor='w')
            self.row_5_frame.pack(pady=(40, 0))

    def on_key_press(self, key):
        if self.choose_pos_var and key == Key.esc:
            self.click_pos_lbl.config(text=self.click_pos_old, fg='white')
            self.choose_pos_var = False
        elif self.is_binding_key:
            if key == Key.esc:
                self.is_binding_key = False
                self.keybind_input.config(text=self.keybind_old, fg='white')
                self.keyboard_keybind_input.config(text=self.keybind_old, fg='white')
                self.row_6_frame.pack_forget()
            elif str(key) != str(self.keyboard_button) and self.device_var.get() == 'Keyboard':
                self.is_binding_key = False
                self.keybind = key
                self.row_6_frame.pack_forget()
                if isinstance(key, keyboard.Key):
                    self.keybind_input.config(text=key.name.capitalize(), fg='white')
                    self.keyboard_keybind_input.config(text=key.name.capitalize(), fg='white')
                else:
                    self.keybind_input.config(text=key.char.capitalize() if hasattr(key, 'char') else key.name.capitalize(), fg='white')
                    self.keyboard_keybind_input.config(text=key.char.capitalize() if hasattr(key, 'char') else key.name.capitalize(), fg='white')
            elif self.device_var.get() == 'Mouse':
                self.is_binding_key = False
                self.keybind = key
                self.row_6_frame.pack_forget()
                if isinstance(key, keyboard.Key):
                    self.keybind_input.config(text=key.name.capitalize(), fg='white')
                    self.keyboard_keybind_input.config(text=key.name.capitalize(), fg='white')
                else:
                    self.keybind_input.config(text=key.char.capitalize() if hasattr(key, 'char') else key.name.capitalize(), fg='white')
                    self.keyboard_keybind_input.config(text=key.char.capitalize() if hasattr(key, 'char') else key.name.capitalize(), fg='white')
            elif str(key) == str(self.keyboard_button):
                self.is_binding_key = False
                self.warning_msg.config(text='Key CANNOT be the same as key to press', fg='red')
                self.row_6_frame.pack()
                self.keybind_input.config(text=self.keybind_old, fg='white')
                self.keyboard_keybind_input.config(text=self.keybind_old, fg='white')
                self.keybind = None
        elif key == self.keybind and not self.button_press:
            self.is_running = not self.is_running
            if self.is_running:
                self.start_clicker()
        elif self.button_press:
            if key == Key.esc:
                self.keyboard_key_lbl.config(text=self.click_keyboard_old, fg='black')
                self.button_press = False
                self.row_6_frame.pack_forget()
            elif key != self.keybind:
                if self.keyboard_key_lbl.cget("text") != 'Key CANNOT be the same as keybind':
                    self.keyboard_button = key
                    self.button_press = False
                    self.row_6_frame.pack_forget()
                    if isinstance(key, keyboard.Key):
                        self.keyboard_key_lbl.config(text=key.name.capitalize(), fg='black')
                    else:
                        self.keyboard_key_lbl.config(text=key.char.capitalize() if hasattr(key, 'char') else key.name.capitalize(), fg='black')
            else:
                self.button_press = False
                self.keyboard_key_lbl.config(text=self.click_keyboard_old, fg='black')
                self.warning_msg.config(text='Key CANNOT be the same as keybind', fg='red')
                self.row_6_frame.pack()
                self.keyboard_button = None

    def start_clicker(self):
        self.is_running = True
        if self.click_thread is None or not self.click_thread.is_alive() and self.device_var.get() == 'Mouse':
            self.cps = int(self.cps_var.get())
            if self.button_var.get() == "Left":
                self.button = Button.left
            elif self.button_var.get() == "Right":
                self.button = Button.right
            elif self.button_var.get() == "Middle":
                self.button = Button.middle
            self.click_thread = threading.Thread(target=self.run_clicker)
            self.click_thread.start()
        if self.click_thread is None or not self.click_thread.is_alive() and self.device_var.get() == 'Keyboard':
            self.cps = int(self.cps_var.get())
            self.click_thread = threading.Thread(target=self.run_clicker)
            self.click_thread.start()

    def stop_clicker(self):
        self.is_running = False

    def run_clicker(self):
        while self.is_running:
            if self.device_var.get() == 'Mouse':
                if self.click_type_var.get() == 'Single Click':
                    if self.pos_var.get() == 'Pick Location':
                        self.mouse.position = self.pos
                    self.mouse.press(self.button)
                    self.mouse.release(self.button)
                    time.sleep(1/self.cps)
                elif self.click_type_var.get() == 'Double Click':
                    for i in range(2):
                        if self.pos_var.get() == 'Pick Location':
                            self.mouse.position = self.pos
                        self.mouse.press(self.button)
                        self.mouse.release(self.button)
                    time.sleep(1/self.cps)
                else:
                    for i in range(3):
                        if self.pos_var.get() == 'Pick Location':
                            self.mouse.position = self.pos
                        self.mouse.press(self.button)
                        self.mouse.release(self.button)
                    time.sleep(1/self.cps)
            elif self.device_var.get() == 'Keyboard':
                if self.press_type_var.get() == 'Single Press':
                    self.keyboard.press(self.keyboard_button)
                    self.keyboard.release(self.keyboard_button)
                    time.sleep(1/self.cps)
                elif self.press_type_var.get() == 'Double Press':
                    for i in range(2):
                        if self.pos_var.get() == 'Pick Press':
                            self.mouse.position = self.pos
                        self.keyboard.press(self.keyboard_button)
                        self.keyboard.release(self.keyboard_button)
                    time.sleep(1/self.cps)
                else:
                    for i in range(3):
                        self.keyboard.press(self.keyboard_button)
                        self.keyboard.release(self.keyboard_button)
                    time.sleep(1/self.cps)
        while self.is_running:
            if self.pos_var.get() == 'Pick Location':
                self.mouse.position = self.pos

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    autoclicker = AutoClicker()
    autoclicker.run()