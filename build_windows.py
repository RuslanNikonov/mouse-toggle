#!/usr/bin/env python3
"""
Скрипт для сборки mouse_toggle.py в exe для Windows
Запускать на Windows с установленным Python
"""

import subprocess
import sys
import os

def build():
    # Устанавливаем зависимости для сборки
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller", "pynput"])
    
    # Собираем exe
    cmd = [
        "pyinstaller",
        "--onefile",           # Один файл
        "--windowed",          # Без консоли (можно убрать для отладки)
        "--name", "MouseToggle",
        "--clean",
        "mouse_toggle.py"
    ]
    
    subprocess.check_call(cmd)
    
    print("\n" + "="*50)
    print("Сборка завершена!")
    print("EXE файл: dist/MouseToggle.exe")
    print("="*50)

if __name__ == "__main__":
    build()
