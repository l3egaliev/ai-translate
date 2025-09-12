import requests
from config import OPENAI_API_KEY, OPENAI_BASE_URL, MODEL_NAME, DEEPL_API_KEY
from settings import load_settings

# Попробуем импортировать deepl
try:
    import deepl
    HAS_DEEPL = True
except ImportError:
    HAS_DEEPL = False

def _normalize_deepl_target_lang(target_language_code):
    """Normalize ambiguous or deprecated DeepL target language codes.

    DeepL deprecates "EN" and "PT" without region. Default to EN-US and PT-BR.
    Leave other valid codes unchanged (e.g., ZH, ZH-TW, EN-GB, EN-US, PT-PT, PT-BR, etc.).
    """
    if not target_language_code:
        return target_language_code
    code_upper = str(target_language_code).upper()
    if code_upper == "EN":
        return "EN-US"
    if code_upper == "PT":
        return "PT-BR"
    return code_upper

def translate_text(text, target_language, target_language_code=None):
    # Если есть DeepL и API ключ — используем DeepL
    if HAS_DEEPL and target_language_code and DEEPL_API_KEY and DEEPL_API_KEY != "YOUR_DEEPL_API_KEY_HERE":
        try:
            translator = deepl.Translator(DEEPL_API_KEY)
            deepl_target = _normalize_deepl_target_lang(target_language_code)
            result = translator.translate_text(text, target_lang=deepl_target)
            return result.text
        except Exception as e:
            return f"[DeepL error] {e}"
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
