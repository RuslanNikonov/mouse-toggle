#!/usr/bin/env python3
"""
Mouse Toggle GUI - программа для имитации зажатия кнопки мыши.
С поддержкой выбора горячей клавиши и выбора кнопки мыши.
"""

import sys
import platform
import tkinter as tk
from tkinter import ttk, messagebox
from pynput import keyboard, mouse
from pynput.mouse import Button
from threading import Thread

IS_WINDOWS = platform.system() == 'Windows'
IS_MAC = platform.system() == 'Darwin'

MOUSE_BUTTONS = {
    'ЛКМ (Левая)': Button.left,
    'ПКМ (Правая)': Button.right,
    'СКМ (Средняя)': Button.middle
}

HOTKEY_OPTIONS = [
    'X', 'Z', 'C', 'V', 'B', 'N', 'M',
    'F', 'G', 'H', 'J', 'K', 'L',
    'Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P',
    '1', '2', '3', '4', '5', '6', '7', '8', '9', '0',
    'Space', 'Tab', 'Caps Lock', 'Shift', 'Ctrl', 'Alt',
    'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12'
]


class MouseToggleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Mouse Toggle")
        self.root.geometry("400x350")
        self.root.resizable(False, False)
        
        # Переменные состояния
        self.is_running = False
        self.is_pressed = False
        self.listener = None
        self.mouse_controller = mouse.Controller()
        
        # Настройки по умолчанию
        self.hotkey = tk.StringVar(value='X')
        self.mouse_button = tk.StringVar(value='ЛКМ (Левая)')
        self.status_text = tk.StringVar(value="Готово к запуску")
        
        self.create_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def create_ui(self):
        # Заголовок
        title = ttk.Label(self.root, text="Mouse Toggle", font=('Arial', 16, 'bold'))
        title.pack(pady=10)
        
        # Фрейм настроек
        settings_frame = ttk.LabelFrame(self.root, text="Настройки", padding=10)
        settings_frame.pack(padx=20, pady=5, fill='x')
        
        # Выбор горячей клавиши
        ttk.Label(settings_frame, text="Горячая клавиша:").grid(row=0, column=0, sticky='w', pady=5)
        self.hotkey_combo = ttk.Combobox(settings_frame, textvariable=self.hotkey, 
                                         values=HOTKEY_OPTIONS, state='readonly', width=15)
        self.hotkey_combo.grid(row=0, column=1, padx=5, pady=5)
        
        # Выбор кнопки мыши
        ttk.Label(settings_frame, text="Кнопка мыши:").grid(row=1, column=0, sticky='w', pady=5)
        self.mouse_combo = ttk.Combobox(settings_frame, textvariable=self.mouse_button,
                                        values=list(MOUSE_BUTTONS.keys()), state='readonly', width=15)
        self.mouse_combo.grid(row=1, column=1, padx=5, pady=5)
        
        # Статус
        status_frame = ttk.LabelFrame(self.root, text="Статус", padding=10)
        status_frame.pack(padx=20, pady=10, fill='x')
        
        self.status_label = ttk.Label(status_frame, textvariable=self.status_text, 
                                     font=('Arial', 11))
        self.status_label.pack()
        
        # Индикатор
        self.indicator = tk.Canvas(status_frame, width=20, height=20, highlightthickness=0)
        self.indicator.pack(pady=5)
        self.indicator_circle = self.indicator.create_oval(2, 2, 18, 18, fill='gray')
        
        # Кнопки управления
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=15)
        
        self.start_btn = ttk.Button(btn_frame, text="Запустить", command=self.start, width=12)
        self.start_btn.pack(side='left', padx=5)
        
        self.stop_btn = ttk.Button(btn_frame, text="Остановить", command=self.stop, width=12, state='disabled')
        self.stop_btn.pack(side='left', padx=5)
        
        # Инструкция
        ttk.Label(self.root, text="Нажмите выбранную клавишу для переключения", 
                 font=('Arial', 9), foreground='gray').pack(pady=5)
        
    def get_key_obj(self, key_name):
        """Преобразует название клавиши в объект Key или KeyCode"""
        special_keys = {
            'Space': keyboard.Key.space,
            'Tab': keyboard.Key.tab,
            'Caps Lock': keyboard.Key.caps_lock,
            'Shift': keyboard.Key.shift,
            'Ctrl': keyboard.Key.ctrl,
            'Alt': keyboard.Key.alt,
            'F1': keyboard.Key.f1, 'F2': keyboard.Key.f2, 'F3': keyboard.Key.f3,
            'F4': keyboard.Key.f4, 'F5': keyboard.Key.f5, 'F6': keyboard.Key.f6,
            'F7': keyboard.Key.f7, 'F8': keyboard.Key.f8, 'F9': keyboard.Key.f9,
            'F10': keyboard.Key.f10, 'F11': keyboard.Key.f11, 'F12': keyboard.Key.f12,
        }
        
        if key_name in special_keys:
            return special_keys[key_name]
        else:
            # Обычная буква или цифра
            return keyboard.KeyCode.from_char(key_name.lower())
    
    def on_press(self, key):
        """Обработчик нажатия клавиши"""
        target_key = self.get_key_obj(self.hotkey.get())
        
        # Проверяем совпадение клавиши
        keys_match = False
        
        if isinstance(target_key, keyboard.Key):
            # Специальная клавиша (Shift, Ctrl, etc.)
            if key == target_key:
                keys_match = True
        else:
            # Обычная буква/цифра
            if hasattr(key, 'char') and key.char:
                if key.char.lower() == target_key.char.lower():
                    keys_match = True
            # Проверка по виртуальному коду для кросс-платформенности
            elif hasattr(key, 'vk') and hasattr(target_key, 'vk'):
                if key.vk == target_key.vk:
                    keys_match = True
        
        if keys_match:
            self.toggle_mouse()
    
    def toggle_mouse(self):
        """Переключает состояние кнопки мыши"""
        button = MOUSE_BUTTONS[self.mouse_button.get()]
        
        if self.is_pressed:
            self.mouse_controller.release(button)
            self.is_pressed = False
            self.update_status("Кнопка ОТПУЩЕНА", 'red')
        else:
            self.mouse_controller.press(button)
            self.is_pressed = True
            self.update_status("Кнопка ЗАЖАТА", 'green')
    
    def update_status(self, text, color):
        """Обновляет статус и индикатор"""
        self.status_text.set(text)
        self.indicator.itemconfig(self.indicator_circle, fill=color)
        self.root.update()
    
    def start(self):
        """Запускает прослушивание клавиш"""
        if self.is_running:
            return
            
        self.is_running = True
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        self.hotkey_combo.config(state='disabled')
        self.mouse_combo.config(state='disabled')
        
        self.update_status("Ожидание нажатия...", 'yellow')
        
        # Запускаем слушатель в отдельном потоке
        self.listener_thread = Thread(target=self.run_listener, daemon=True)
        self.listener_thread.start()
    
    def run_listener(self):
        """Запускает keyboard listener"""
        with keyboard.Listener(on_press=self.on_press) as listener:
            self.listener = listener
            listener.join()
    
    def stop(self):
        """Останавливает программу"""
        if not self.is_running:
            return
            
        # Отпускаем кнопку если зажата
        if self.is_pressed:
            button = MOUSE_BUTTONS[self.mouse_button.get()]
            self.mouse_controller.release(button)
            self.is_pressed = False
        
        # Останавливаем слушатель
        if self.listener:
            self.listener.stop()
            self.listener = None
        
        self.is_running = False
        
        # Возвращаем UI в исходное состояние
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.hotkey_combo.config(state='readonly')
        self.mouse_combo.config(state='readonly')
        self.update_status("Готово к запуску", 'gray')
    
    def on_closing(self):
        """Обработчик закрытия окна"""
        self.stop()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = MouseToggleApp(root)
    root.mainloop()
