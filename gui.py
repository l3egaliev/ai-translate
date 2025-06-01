from PyQt5.QtWidgets import (
    QWidget, QLabel, QTextEdit, QComboBox, QPushButton, QVBoxLayout,
    QSystemTrayIcon, QMenu, QAction, QMessageBox, QApplication, QHBoxLayout,
    QFrame, QSizePolicy, QStackedWidget, QListWidget, QListWidgetItem
)
from PyQt5.QtGui import QIcon, QFont, QPalette, QColor, QPainter, QPen
from PyQt5.QtCore import Qt, QTimer, QRect
from settings import load_settings, save_settings
from translator import translate_text
import os
import numpy as np

class LoadingSpinner(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(32, 32)
        self.angle = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.rotate)
        self.hide()

    def rotate(self):
        self.angle = (self.angle + 1) % 8
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        center = self.rect().center()
        radius = 12
        dot_radius = 3
        color = QColor("#2196F3")
        for i in range(8):
            alpha = 150 + 105 * ((i + self.angle) % 8) // 7  # плавная прозрачность
            color.setAlpha(alpha)
            painter.setBrush(color)
            painter.setPen(Qt.NoPen)
            angle_rad = (i * 45) * 3.14159 / 180
            x = center.x() + radius * float(np.cos(angle_rad))
            y = center.y() + radius * float(np.sin(angle_rad))
            painter.drawEllipse(int(x - dot_radius), int(y - dot_radius), dot_radius * 2, dot_radius * 2)

    def start(self):
        self.show()
        self.timer.start(80)

    def stop(self):
        self.hide()
        self.timer.stop()

class ModernButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 15px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
            QPushButton:disabled {
                background-color: #BDBDBD;
            }
        """)

class ModernComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QComboBox {
                border: 1px solid #BDBDBD;
                border-radius: 8px;
                padding: 8px;
                background: white;
                font-size: 15px;
            }
            QComboBox::drop-down {
                border: none;
            }
        """)

class ModernTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QTextEdit {
                border: 1px solid #BDBDBD;
                border-radius: 8px;
                padding: 12px;
                background: white;
                font-size: 15px;
            }
        """)

class Sidebar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(180)
        self.setStyleSheet("""
            QFrame {
                background: #F3F6FA;
                border-top-right-radius: 20px;
                border-bottom-right-radius: 20px;
            }
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 30, 0, 30)
        layout.setSpacing(20)
        self.list = QListWidget()
        self.list.setStyleSheet("""
            QListWidget {
                background: transparent;
                border: none;
                font-size: 16px;
            }
            QListWidget::item {
                padding: 16px 10px;
                border-radius: 8px;
                margin: 4px 8px;
            }
            QListWidget::item:selected {
                background: #2196F3;
                color: white;
            }
        """)
        self.list.setFrameShape(QFrame.NoFrame)
        self.list.setSpacing(4)
        self.list.addItem(QListWidgetItem(QIcon("icon.png"), "Перевод"))
        self.list.addItem(QListWidgetItem(QIcon("icon.png"), "История"))
        self.list.setCurrentRow(0)
        layout.addWidget(self.list)
        layout.addStretch()

class TranslatorPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = load_settings()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(25)
        title = QLabel("AI Переводчик")
        title.setFont(QFont("Segoe UI", 22, QFont.Bold))
        title.setStyleSheet("color: #222; margin-bottom: 10px;")
        layout.addWidget(title)

        lang_layout = QHBoxLayout()
        self.lang_select = ModernComboBox()
        self.lang_select.addItems(["английский", "немецкий", "французский", "испанский"])
        self.lang_select.setCurrentText(self.settings.get("last_language", "английский"))
        self.lang_select.currentTextChanged.connect(self.save_language_choice)
        lang_layout.addWidget(QLabel("Перевести на:"))
        lang_layout.addWidget(self.lang_select)
        lang_layout.addStretch()
        layout.addLayout(lang_layout)

        self.text_input = ModernTextEdit()
        self.text_input.setPlaceholderText("Введите текст для перевода...")
        self.text_input.setMinimumHeight(120)
        layout.addWidget(self.text_input)

        button_layout = QHBoxLayout()
        self.translate_button = ModernButton("Перевести")
        self.translate_button.clicked.connect(self.perform_translation)
        self.loading_spinner = LoadingSpinner()
        button_layout.addWidget(self.translate_button)
        button_layout.addWidget(self.loading_spinner)
        button_layout.addStretch()
        self.clear_button = ModernButton("Очистить")
        self.clear_button.clicked.connect(self.clear_fields)
        self.clear_button.setStyleSheet(self.clear_button.styleSheet().replace("#2196F3", "#F44336"))
        button_layout.addWidget(self.clear_button)
        layout.addLayout(button_layout)

        self.text_output = ModernTextEdit()
        self.text_output.setReadOnly(True)
        self.text_output.setPlaceholderText("Здесь появится перевод...")
        self.text_output.setMinimumHeight(120)
        layout.addWidget(self.text_output)

    def save_language_choice(self, lang):
        self.settings["last_language"] = lang
        save_settings(self.settings)

    def clear_fields(self):
        self.text_input.clear()
        self.text_output.clear()

    def perform_translation(self):
        text = self.text_input.toPlainText()
        if not text.strip():
            QMessageBox.warning(self, "Предупреждение", "Введите текст для перевода")
            return
        target_lang = self.lang_select.currentText()
        self.translate_button.setEnabled(False)
        self.translate_button.setText("Перевожу...")
        self.loading_spinner.start()
        try:
            translated = translate_text(text, target_lang)
            self.text_output.setPlainText(translated)
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось выполнить перевод: {e}")
        finally:
            self.translate_button.setEnabled(True)
            self.translate_button.setText("Перевести")
            self.loading_spinner.stop()

class HistoryPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(25)
        title = QLabel("История переводов")
        title.setFont(QFont("Segoe UI", 22, QFont.Bold))
        title.setStyleSheet("color: #222; margin-bottom: 10px;")
        layout.addWidget(title)
        self.text_area = ModernTextEdit()
        self.text_area.setReadOnly(True)
        try:
            with open("history.txt", "r", encoding="utf-8") as f:
                content = f.read()
        except FileNotFoundError:
            content = "История пока пуста."
        self.text_area.setText(content)
        layout.addWidget(self.text_area)
        self.clear_button = ModernButton("Очистить историю")
        self.clear_button.setStyleSheet(self.clear_button.styleSheet().replace("#2196F3", "#F44336"))
        self.clear_button.clicked.connect(self.clear_history)
        layout.addWidget(self.clear_button)

    def clear_history(self):
        reply = QMessageBox.question(self, "Подтверждение", "Вы уверены, что хотите очистить историю?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                with open("history.txt", "w", encoding="utf-8") as f:
                    f.write("")
                self.text_area.setText("История очищена.")
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Не удалось очистить историю: {e}")

class TranslatorGUI(QWidget):
    def __init__(self, input_text=""):
        super().__init__()
        self.setWindowTitle("AI Переводчик")
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        self.setWindowIcon(QIcon("icon.png"))
        self.setStyleSheet("""
            QWidget {
                background-color: #F5F5F5;
                font-family: 'Segoe UI', Arial;
            }
        """)
        self.sidebar = Sidebar()
        self.stack = QStackedWidget()
        self.translator_page = TranslatorPage()
        self.history_page = HistoryPage()
        self.stack.addWidget(self.translator_page)
        self.stack.addWidget(self.history_page)
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.stack)
        self.sidebar.list.currentRowChanged.connect(self.stack.setCurrentIndex)
        self.init_tray_icon()

    def init_tray_icon(self):
        self.tray_icon = QSystemTrayIcon(QIcon("icon.png"), parent=self)
        tray_menu = QMenu()
        show_action = QAction("Открыть", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)
        quit_action = QAction("Выход", self)
        quit_action.triggered.connect(QApplication.instance().quit)
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "AI Переводчик",
            "Приложение свернуто в трей. Щелкните по иконке для открытия.",
            QSystemTrayIcon.Information,
            3000
        )
