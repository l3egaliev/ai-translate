import PyInstaller.__main__
import os

# Получаем текущую директорию
current_dir = os.path.dirname(os.path.abspath(__file__))

PyInstaller.__main__.run([
    'main.py',  # Основной файл приложения
    '--name=AI_Translator',  # Имя выходного файла
    '--onefile',  # Создать один исполняемый файл
    '--windowed',  # Не показывать консоль
    '--icon=icon.ico',  # Иконка приложения
    '--add-data=icon.ico;.',  # Добавить иконку в ресурсы
    '--clean',  # Очистить кэш перед сборкой
    '--noconfirm',  # Не спрашивать подтверждения
    f'--distpath={os.path.join(current_dir, "dist")}',  # Путь для выходного файла
    f'--workpath={os.path.join(current_dir, "build")}',  # Путь для временных файлов
    '--hidden-import=PyQt5',
    '--hidden-import=keyboard',
    '--hidden-import=pyperclip',
    '--hidden-import=requests',
    '--hidden-import=win32gui',
    '--hidden-import=win32con',
    '--hidden-import=win32clipboard',
    '--hidden-import=win32api',
    '--hidden-import=numpy',
    '--hidden-import=googletrans',
    '--hidden-import=openai',
]) 