import sys
from PyQt5.QtWidgets import QApplication
from qt_material import apply_stylesheet
from global_hotkey import start_hotkey_listener
from gui import TranslatorGUI

app = QApplication(sys.argv)
apply_stylesheet(app, theme='light_blue.xml')

# Запускаем обработчик горячих клавиш
hotkey_handler = start_hotkey_listener()

# Создаем основное окно, передавая hotkey_handler
main_window = TranslatorGUI(hotkey_handler=hotkey_handler)
main_window.show()

# Подключаем обработчик текста
def handle_copied_text(text):
    main_window.stack.setCurrentIndex(1)  # Переключаемся на страницу перевода
    main_window.translator_page.text_input.setText(text)
    main_window.show()
    main_window.activateWindow()

hotkey_handler.text_copied.connect(handle_copied_text)

sys.exit(app.exec_())
