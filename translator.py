import requests
from config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, MODEL_NAME

def translate_text(text, target_language):
    source_lang = detect_language(text)
    prompt = f"""Переведи текст с {source_lang} на {target_language}. 
Верни ТОЛЬКО перевод, без пояснений и дополнительного текста.
Текст для перевода:

{text}"""

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",
        "X-Title": "Desktop Translator"
    }

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": "Ты профессиональный переводчик. Возвращай ТОЛЬКО перевод, без пояснений и дополнительного текста."},
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post(f"{OPENROUTER_BASE_URL}/chat/completions", headers=headers, json=payload)

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"].strip()
    else:
        return f"[Ошибка: {response.status_code}]\n{response.text}"


def detect_language(text):
    prompt = f"Определи, на каком языке написан этот текст. Ответь одним словом: Русский, Английский и т.п.\n\n{text}"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",
        "X-Title": "Desktop Translator"
    }
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": "Ты определяешь язык текста. Ответь одним словом: Русский, Английский и т.п."},
            {"role": "user", "content": prompt}
        ]
    }
    response = requests.post(f"{OPENROUTER_BASE_URL}/chat/completions", headers=headers, json=payload)

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"].strip()
    else:
        return "Неизвестно"

def save_history(source, target, result):
    with open("history.txt", "a", encoding="utf-8") as f:
        f.write(f"[{source} → {target}]\n")
        f.write(f"Исходный текст:\n{source}\n")
        f.write(f"Перевод:\n{result}\n\n---\n\n")
