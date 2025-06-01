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
        self.current_hotkey = None
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

    def setup_hotkey(self, hotkey=None):
        if hotkey is None:
            from settings import load_settings
            hotkey = load_settings().get("hotkey", "ctrl+shift+t")
        if self.current_hotkey:
            keyboard.remove_hotkey(self.current_hotkey)
        def on_hotkey():
            print("🔥 Горячая клавиша сработала")
            text = self.copy_selected_text()
            print(f"📋 Скопировано: '{text}'")
            if text.strip():
                self.text_copied.emit(text)
            else:
                print("⚠️ Нет выделенного текста")
        self.current_hotkey = keyboard.add_hotkey(hotkey, on_hotkey, suppress=True)
        print(f"🟢 Глобальный переводчик активен. Нажмите {hotkey.upper()} для копирования выделенного текста.")

    def set_hotkey(self, hotkey):
        self.setup_hotkey(hotkey)

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
