import json
import os

SETTINGS_FILE = "settings.json"

def clean_surrogates(obj):
    if isinstance(obj, str):
        # Заменяем некорректные суррогаты на символы-заполнители
        return obj.encode('utf-16', 'surrogatepass').decode('utf-16', 'replace')
    elif isinstance(obj, dict):
        return {k: clean_surrogates(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_surrogates(i) for i in obj]
    else:
        return obj

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            # Если файл повреждён — возвращаем пустой словарь
            return {}
    return {}

def save_settings(settings):
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            clean = clean_surrogates(settings)
            json.dump(clean, f, indent=2, ensure_ascii=False)
    except UnicodeEncodeError as e:
        print(f"[Ошибка сохранения настроек] Некорректные символы: {e}. Очищаю settings.json.")
        # Очищаем settings.json
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[Ошибка сохранения настроек] {e}")
