import keyboard
import pyperclip
import threading
from gui import TranslatorGUI
from PyQt5.QtWidgets import QApplication
import sys
from config import HOTKEY

def listen_hotkey():
    def on_trigger():
        # Эмулируем Ctrl+C (копируем выделенный текст)
        keyboard.press_and_release("ctrl+c")
        # Небольшая задержка
        import time; time.sleep(0.2)
        text = pyperclip.paste()

        app = QApplication(sys.argv)
        window = TranslatorGUI(text)
        window.show()
        app.exec_()

    keyboard.add_hotkey(HOTKEY, on_trigger)
    print(f"[OK] Ожидание горячей клавиши: {HOTKEY}")
    keyboard.wait()
