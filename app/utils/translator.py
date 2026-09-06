# app/utils/translator.py
from functools import lru_cache
from flask import session, has_request_context
from flask_babel import get_locale
import argostranslate.package
import argostranslate.translate

def ensure_language_installed():
    """
    Checks if the English-to-Spanish package is installed.
    Downloads and installs it automatically if missing.
    """
    try:
        installed_languages = argostranslate.translate.get_installed_languages()
        en_lang = next((l for l in installed_languages if l.code == 'en'), None)
        es_lang = next((l for l in installed_languages if l.code == 'es'), None)

        if en_lang and es_lang:
            translation = en_lang.get_translation(es_lang)
            if translation:
                return  # Package already installed

        print("Downloading Argos Translate English-to-Spanish package...")
        argostranslate.package.update_package_index()
        available = argostranslate.package.get_available_packages()
        pkg = next(filter(lambda x: x.from_code == "en" and x.to_code == "es", available))
        download_path = pkg.download()
        argostranslate.package.install_from_path(download_path)
        print("Argos Translate EN -> ES package installed successfully.")
    except Exception as e:
        print(f"Argos Translate setup error: {e}")

# Run model check on module import
ensure_language_installed()

@lru_cache(maxsize=2048)
def _translate_to_spanish(text):
    """
    Translates English text to Spanish locally.
    lru_cache prevents re-processing identical strings.
    """
    if not text or not str(text).strip():
        return text or ""

    try:
        return argostranslate.translate.translate(str(text).strip(), "en", "es")
    except Exception as e:
        print(f"Argos Translation Error: {e}")
        return text


def translate_dynamic(text):
    """
    Jinja filter function. Checks active language and translates
    dynamic text ONLY when session language is Spanish ('es').
    """
    if not text or not str(text).strip():
        return text or ""

    lang = 'en'
    if has_request_context() and session.get('lang'):
        lang = session.get('lang')
    else:
        try:
            lang = str(get_locale())
        except Exception:
            lang = 'en'

    if str(lang).startswith('es'):
        return _translate_to_spanish(str(text))

    return text