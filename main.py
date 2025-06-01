import sys
from PyQt5.QtWidgets import QApplication
from global_hotkey import start_hotkey_listener
from gui import TranslatorGUI

app = QApplication(sys.argv)

# Создаем основное окно
main_window = TranslatorGUI()
main_window.show()

# Запускаем обработчик горячих клавиш
hotkey_handler = start_hotkey_listener()

# Подключаем обработчик текста
def handle_copied_text(text):
    main_window.stack.setCurrentIndex(0)  # Переключаемся на страницу перевода
    main_window.translator_page.text_input.setText(text)
    main_window.show()
    main_window.activateWindow()

hotkey_handler.text_copied.connect(handle_copied_text)

sys.exit(app.exec_())
