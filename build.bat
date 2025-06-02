@echo off
echo Installing requirements...
pip install -r requirements.txt

echo Building application...
python build.py

echo Done! Check the dist folder for AI_Translator.exe
pause 