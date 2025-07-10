import sys
import os
from PyQt5.QtWidgets import (
    QWidget, QLabel, QTextEdit, QComboBox, QPushButton, QVBoxLayout,
    QSystemTrayIcon, QMenu, QAction, QMessageBox, QApplication, QHBoxLayout,
    QFrame, QSizePolicy, QStackedWidget, QListWidget, QListWidgetItem, QInputDialog, QDialog
)
from PyQt5.QtGui import QIcon, QFont, QPalette, QColor, QPainter, QPen, QKeySequence
from PyQt5.QtCore import Qt, QTimer, QRect, QRunnable, QThreadPool, pyqtSignal, QObject, QPoint
from settings import load_settings, save_settings
from translator import translate_text
import numpy as np

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temporary folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

LANGUAGES = [
    ("English", "en"),
    ("Russian", "ru"),
    ("Spanish", "es"),
    ("Chinese", "zh"),
    ("Hindi", "hi"),
    ("Arabic", "ar"),
    ("Portuguese", "pt"),
    ("Bengali", "bn"),
    ("Japanese", "ja"),
    ("Kazakh", "kk"),
    ("Kyrgyz", "ky"),
    ("Uzbek", "uz"),
    ("German", "de"),
    ("French", "fr"),
    ("Italian", "it"),
    ("Turkish", "tr"),
    ("Korean", "ko"),
    ("Vietnamese", "vi"),
    ("Polish", "pl"),
    ("Dutch", "nl"),
    ("Ukrainian", "uk"),
    ("Persian", "fa"),
    ("Indonesian", "id"),
]

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
        self.list.addItem(QListWidgetItem(QIcon(resource_path("icon.png")), "Translate"))
        self.list.addItem(QListWidgetItem(QIcon(resource_path("icon.png")), "Settings"))
        self.list.setCurrentRow(0)
        layout.addWidget(self.list)
        layout.addStretch()

class HotkeyCaptureDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("New hotkey")
        self.setModal(True)
        self.setFixedSize(320, 100)
        layout = QVBoxLayout(self)
        self.label = QLabel("Press new combination…")
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)
        self.hotkey = None

    def keyPressEvent(self, event):
        seq = QKeySequence(int(event.modifiers()) + event.key())
        text = seq.toString().lower()
        if text and text != "unknown key":
            self.hotkey = text
            self.accept()

class TranslateWorkerSignals(QObject):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

class TranslateWorker(QRunnable):
    def __init__(self, text, target_lang_name, target_lang_code):
        super().__init__()
        self.text = text
        self.target_lang_name = target_lang_name
        self.target_lang_code = target_lang_code
        self.signals = TranslateWorkerSignals()

    def run(self):
        try:
            translated = translate_text(self.text, self.target_lang_name, self.target_lang_code)
            self.signals.finished.emit(translated)
        except Exception as e:
            self.signals.error.emit(str(e))

class TranslatorPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = load_settings()
        self.threadpool = QThreadPool()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(25)
        # Заголовок и кнопка How to use
        title_layout = QHBoxLayout()
        title = QLabel("AI Translator")
        title.setFont(QFont("Segoe UI", 22, QFont.Bold))
        title.setStyleSheet("color: #222; margin-bottom: 10px;")
        title_layout.addWidget(title)
        title_layout.addStretch()
        self.howto_button = ModernButton("How to use")
        self.howto_button.setStyleSheet(self.howto_button.styleSheet().replace("#2196F3", "#4CAF50"))
        self.howto_button.clicked.connect(self.show_howto)
        title_layout.addWidget(self.howto_button)
        layout.addLayout(title_layout)

        lang_layout = QHBoxLayout()
        self.lang_select = ModernComboBox()
        self.lang_select.addItems([name for name, code in LANGUAGES])
        self.lang_select.setCurrentText(self.settings.get("last_language", "English"))
        self.lang_select.currentTextChanged.connect(self.save_language_choice)
        lang_layout.addWidget(QLabel("Translate to:"))
        lang_layout.addWidget(self.lang_select)
        lang_layout.addStretch()
        layout.addLayout(lang_layout)

        self.text_input = ModernTextEdit()
        self.text_input.setPlaceholderText("Enter text to translate...")
        self.text_input.setMinimumHeight(120)
        layout.addWidget(self.text_input)

        button_layout = QHBoxLayout()
        self.translate_button = ModernButton("Translate")
        self.translate_button.clicked.connect(self.perform_translation)
        self.loading_spinner = LoadingSpinner()
        button_layout.addWidget(self.translate_button)
        button_layout.addWidget(self.loading_spinner)
        button_layout.addStretch()
        self.clear_button = ModernButton("Clear")
        self.clear_button.clicked.connect(self.clear_fields)
        self.clear_button.setStyleSheet(self.clear_button.styleSheet().replace("#2196F3", "#F44336"))
        button_layout.addWidget(self.clear_button)
        layout.addLayout(button_layout)

        # Output + Copy button
        output_layout = QHBoxLayout()
        self.text_output = ModernTextEdit()
        self.text_output.setReadOnly(True)
        self.text_output.setPlaceholderText("Translation will appear here...")
        self.text_output.setMinimumHeight(120)
        output_layout.addWidget(self.text_output)
        self.copy_button = ModernButton("Copy")
        self.copy_button.setStyleSheet(self.copy_button.styleSheet().replace("#2196F3", "#2196F3"))
        self.copy_button.clicked.connect(self.copy_translation)
        output_layout.addWidget(self.copy_button)
        layout.addLayout(output_layout)

    def save_language_choice(self, lang):
        self.settings["last_language"] = lang
        save_settings(self.settings)

    def clear_fields(self):
        self.text_input.clear()
        self.text_output.clear()

    def perform_translation(self):
        text = self.text_input.toPlainText()
        if not text.strip():
            QMessageBox.warning(self, "Warning", "Please enter text to translate")
            return
        target_lang_name = self.lang_select.currentText()
        target_lang_code = next(
            (code for name, code in LANGUAGES if name == target_lang_name),
            None,
        )
        self.translate_button.setEnabled(False)
        self.translate_button.setText("Translating...")
        self.loading_spinner.start()
        worker = TranslateWorker(text, target_lang_name, target_lang_code)
        worker.signals.finished.connect(self.on_translation_finished)
        worker.signals.error.connect(self.on_translation_error)
        self.threadpool.start(worker)

    def on_translation_finished(self, translated):
        self.text_output.setPlainText(translated)
        self.translate_button.setEnabled(True)
        self.translate_button.setText("Translate")
        self.loading_spinner.stop()

    def on_translation_error(self, error):
        QMessageBox.warning(self, "Error", f"Translation failed: {error}")
        self.translate_button.setEnabled(True)
        self.translate_button.setText("Translate")
        self.loading_spinner.stop()

    def copy_translation(self):
        text = self.text_output.toPlainText()
        if text.strip():
            QApplication.clipboard().setText(text)
            QMessageBox.information(self, "Copied", "Translation copied to clipboard!")

    def show_howto(self):
        QMessageBox.information(self, "How to use AI Translator",
            """
<b>How to use AI Translator:</b><br><br>
1. Enter or paste the text you want to translate in the upper field.<br>
2. Select the target language from the dropdown list.<br>
3. Click the <b>Translate</b> button.<br>
4. The translation will appear below. You can copy it by clicking the <b>Copy</b> button.<br>
5. You can change the hotkey and default language in the <b>Settings</b> tab.<br>
6. To quickly translate selected text from any app, use the hotkey (default: <b>Ctrl+Shift+T</b>).<br>
            """
        )

class SettingsPage(QWidget):
    def __init__(self, parent=None, hotkey_handler=None):
        super().__init__(parent)
        self.settings = load_settings()
        self.hotkey_handler = hotkey_handler
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(25)
        title = QLabel("Settings")
        title.setFont(QFont("Segoe UI", 22, QFont.Bold))
        title.setStyleSheet("color: #222; margin-bottom: 10px;")
        layout.addWidget(title)

        # Default language
        lang_layout = QHBoxLayout()
        lang_label = QLabel("Default language:")
        lang_label.setStyleSheet("font-size: 15px;")
        self.lang_combo = ModernComboBox()
        self.lang_combo.addItems([name for name, code in LANGUAGES])
        self.lang_combo.setCurrentText(self.settings.get("last_language", "English"))
        self.lang_combo.currentTextChanged.connect(self.save_language)
        lang_layout.addWidget(lang_label)
        lang_layout.addWidget(self.lang_combo)
        lang_layout.addStretch()
        layout.addLayout(lang_layout)

        # Hotkey
        hotkey_layout = QHBoxLayout()
        hotkey_label = QLabel("Hotkey:")
        hotkey_label.setStyleSheet("font-size: 15px;")
        self.hotkey_display = QLabel(self.settings.get("hotkey", "ctrl+shift+t"))
        self.hotkey_display.setStyleSheet("font-size: 15px; background: #F3F6FA; border-radius: 8px; padding: 6px 16px;")
        self.change_hotkey_btn = ModernButton("Change")
        self.change_hotkey_btn.setStyleSheet(self.change_hotkey_btn.styleSheet().replace("#2196F3", "#FF9800"))
        self.change_hotkey_btn.clicked.connect(self.change_hotkey)
        hotkey_layout.addWidget(hotkey_label)
        hotkey_layout.addWidget(self.hotkey_display)
        hotkey_layout.addWidget(self.change_hotkey_btn)
        hotkey_layout.addStretch()
        layout.addLayout(hotkey_layout)

        layout.addStretch()

    def save_language(self, lang):
        self.settings["last_language"] = lang
        save_settings(self.settings)

    def change_hotkey(self):
        dlg = HotkeyCaptureDialog(self)
        if dlg.exec_() == QDialog.Accepted and dlg.hotkey:
            hotkey = dlg.hotkey
            self.hotkey_display.setText(hotkey)
            self.settings["hotkey"] = hotkey
            save_settings(self.settings)
            if self.hotkey_handler:
                self.hotkey_handler.set_hotkey(hotkey)
            QMessageBox.information(self, "Done", f"Hotkey changed to: {hotkey}")

class TranslatorGUI(QWidget):
    def __init__(self, input_text="", hotkey_handler=None):
        super().__init__()
        self.setWindowTitle("AI Translator")
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        self.setWindowIcon(QIcon(resource_path("icon.png")))
        self.setStyleSheet("""
            QWidget {
                background-color: #F5F5F5;
                font-family: 'Segoe UI', Arial;
            }
        """)
        self.sidebar = Sidebar()
        self.stack = QStackedWidget()
        self.translator_page = TranslatorPage()
        self.hotkey_handler = hotkey_handler
        self.settings_page = SettingsPage(hotkey_handler=self.hotkey_handler)
        self.stack.addWidget(self.translator_page)
        self.stack.addWidget(self.settings_page)
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.stack)
        self.sidebar.list.currentRowChanged.connect(self.stack.setCurrentIndex)
        self.init_tray_icon()

    def init_tray_icon(self):
        self.tray_icon = QSystemTrayIcon(QIcon(resource_path("icon.png")), parent=self)
        tray_menu = QMenu()
        show_action = QAction("Open", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)
        quit_action = QAction("Exit", self)
        quit_action.triggered.connect(QApplication.instance().quit)
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "AI Translator",
            "Application minimized to tray. Click icon to open.",
            QSystemTrayIcon.Information,
            3000
        )
