import requests
from config import OPENAI_API_KEY, OPENAI_BASE_URL, MODEL_NAME

# Попробуем импортировать googletrans
try:
    from googletrans import Translator as GoogleTranslator
    HAS_GOOGLETRANS = True
except ImportError:
    HAS_GOOGLETRANS = False

def translate_text(text, target_language, target_language_code=None):
    # Если есть googletrans и ISO-код — используем Google Translate
    if HAS_GOOGLETRANS and target_language_code:
        try:
            translator = GoogleTranslator()
            result = translator.translate(text, dest=target_language_code)
            return result.text
        except Exception as e:
            return f"[Google Translate error] {e}"
    # Fallback: OpenAI
    source_lang = detect_language(text)
    if target_language_code:
        prompt = f"""
Translate the following text from {source_lang} to {target_language} ({target_language_code}).
- Output ONLY the translation, without any explanations, comments, or extra text.
- Use only the official alphabet of the target language.
- If you do not know the target language, return the original text unchanged.
- Do not transliterate, translate the meaning.

Text to translate:

{text}
"""
    else:
        prompt = f"""
Translate the following text from {source_lang} to {target_language}.
- Output ONLY the translation, without any explanations, comments, or extra text.
- Use only the official alphabet of the target language.
- If you do not know the target language, return the original text unchanged.
- Do not transliterate, translate the meaning.

Text to translate:

{text}
"""

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": "You are a professional translator. Return ONLY the translation, without any explanations or extra text."},
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post(f"{OPENAI_BASE_URL}/chat/completions", headers=headers, json=payload)

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"].strip()
    else:
        return f"[Error: {response.status_code}]\n{response.text}"


def detect_language(text):
    prompt = f"Detect the language of the following text. Reply with a single word (e.g., English, Russian, etc.):\n\n{text}"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": "You are a language detector. Reply with a single word (e.g., English, Russian, etc.)."},
            {"role": "user", "content": prompt}
        ]
    }
    response = requests.post(f"{OPENAI_BASE_URL}/chat/completions", headers=headers, json=payload)

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"].strip()
    else:
        return "Unknown"

def save_history(source, target, result):
    with open("history.txt", "a", encoding="utf-8") as f:
        f.write(f"[{source} → {target}]\n")
        f.write(f"Source text:\n{source}\n")
        f.write(f"Translation:\n{result}\n\n---\n\n")
