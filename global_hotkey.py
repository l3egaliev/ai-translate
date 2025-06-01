import keyboard
import time
from PyQt5.QtCore import QTimer, QObject, pyqtSignal
import win32gui
import win32con
import win32clipboard
import win32api

from PyQt5.QtWidgets import QApplication
from gui import TranslatorGUI  # Импортируйте ваш GUI

# Список для хранения ссылок на окна, чтобы сборщик мусора их не закрыл
translator_windows = []

class HotkeyHandler(QObject):
    text_copied = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setup_hotkey()

    def copy_selected_text(self):
        try:
            # Сохраняем текущее состояние клавиш
            keyboard.release('ctrl+shift+t')
            
            # Эмулируем Ctrl+C
            keyboard.press('ctrl')
            keyboard.press('c')
            keyboard.release('c')
            keyboard.release('ctrl')
            
            time.sleep(0.1)  # Даем время на копирование

            # Получаем текст из буфера обмена
            win32clipboard.OpenClipboard()
            text = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT) if win32clipboard.IsClipboardFormatAvailable(win32con.CF_UNICODETEXT) else ""
            win32clipboard.CloseClipboard()

            return text
        except Exception as e:
            print(f"Ошибка при копировании текста: {e}")
            return ""

    def setup_hotkey(self):
        def on_hotkey():
            print("🔥 Горячая клавиша сработала")
            text = self.copy_selected_text()
            print(f"📋 Скопировано: '{text}'")
            if text.strip():
                self.text_copied.emit(text)
            else:
                print("⚠️ Нет выделенного текста")

        keyboard.add_hotkey("ctrl+shift+t", on_hotkey, suppress=True)
        print("🟢 Глобальный переводчик активен. Нажмите Ctrl+Shift+T для копирования выделенного текста.")

def start_hotkey_listener():
    handler = HotkeyHandler()
    return handler

def show_translator_window(text):
    from gui import TranslatorGUI
    """
    Создает и показывает окно перевода в главном потоке.
    """
    window = TranslatorGUI(input_text=text)
    window.show()
    translator_windows.append(window)
