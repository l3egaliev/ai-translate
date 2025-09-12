import keyboard
import pyperclip
import threading
from gui import TranslatorGUI
from PyQt5.QtWidgets import QApplication
import sys
from config import HOTKEY
from qt_material import apply_stylesheet

def listen_hotkey():
    def on_trigger():
        # Эмулируем Ctrl+C (копируем выделенный текст)
        keyboard.press_and_release("ctrl+c")
        # Небольшая задержка
        import time; time.sleep(0.2)
        text = pyperclip.paste()

        app = QApplication(sys.argv)
        apply_stylesheet(app, theme='light_blue.xml')
        window = TranslatorGUI(text)
        window.stack.setCurrentIndex(1)
        window.show()
        app.exec_()

    keyboard.add_hotkey(HOTKEY, on_trigger)
    print(f"[OK] Ожидание горячей клавиши: {HOTKEY}")
    keyboard.wait()
