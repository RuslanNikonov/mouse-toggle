#!/usr/bin/env python3
"""
Программа для имитации зажатия ЛКМ при нажатии на клавишу X.
Повторное нажатие X отключает зажатие.
"""

import sys
import platform
from pynput import keyboard, mouse
from pynput.mouse import Button

# Определяем ОС для правильной обработки виртуальных кодов клавиш
IS_WINDOWS = platform.system() == 'Windows'
IS_MAC = platform.system() == 'Darwin'

class MouseToggle:
    def __init__(self):
        self.is_pressed = False
        self.mouse_controller = mouse.Controller()
        self.listener = None

    def on_press(self, key):
        try:
            # Отладка: показываем какая клавиша нажата
            if hasattr(key, 'char'):
                print(f"[DEBUG] Нажата клавиша: char='{key.char}', vk={key.vk if hasattr(key, 'vk') else 'N/A'}")
            else:
                print(f"[DEBUG] Специальная клавиша: {key}, vk={key.vk if hasattr(key, 'vk') else 'N/A'}")

            # Проверяем, была ли нажата клавиша 'x', 'X', 'ч' или 'Ч'
            is_trigger = False
            if hasattr(key, 'char') and key.char:
                lower_char = key.char.lower()
                if lower_char in ('x', 'ч'):
                    is_trigger = True
            # Также проверяем по виртуальному коду клавиши
            elif hasattr(key, 'vk') and key.vk:
                # Windows: 88 = X (0x58), macOS: 7 = X
                vk_code = key.vk
                if IS_WINDOWS and vk_code == 88:  # 0x58 = X на Windows
                    is_trigger = True
                elif IS_MAC and vk_code == 7:  # 7 = X на macOS
                    is_trigger = True

            if is_trigger:
                self.toggle_mouse()
        except AttributeError as e:
            print(f"[DEBUG] Ошибка: {e}")
            pass

    def toggle_mouse(self):
        """Переключает состояние ЛКМ (зажато/отпущено)"""
        if self.is_pressed:
            # Отпускаем ЛКМ
            self.mouse_controller.release(Button.left)
            self.is_pressed = False
            print("ЛКМ ОТПУЩЕНА")
        else:
            # Зажимаем ЛКМ
            self.mouse_controller.press(Button.left)
            self.is_pressed = True
            print("ЛКМ ЗАЖАТА (удерживается)")

    def start(self):
        """Запускает слушатель клавиатуры"""
        print("Программа запущена!")
        print("Нажмите 'X' (англ.) или 'Ч' (рус.) для зажатия ЛКМ")
        print("Нажмите 'X' или 'Ч' снова для отпуска ЛКМ")
        print("Нажмите Ctrl+C или закройте терминал для выхода")
        print("-" * 40)

        with keyboard.Listener(on_press=self.on_press) as listener:
            self.listener = listener
            listener.join()

    def stop(self):
        """Останавливает слушатель и отпускает кнопку мыши при необходимости"""
        if self.is_pressed:
            self.mouse_controller.release(Button.left)
            print("\nЛКМ отпущена при выходе")
        if self.listener:
            self.listener.stop()


if __name__ == "__main__":
    app = MouseToggle()
    try:
        app.start()
    except KeyboardInterrupt:
        print("\nПрограмма остановлена")
    finally:
        app.stop()
