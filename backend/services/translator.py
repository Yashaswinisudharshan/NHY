from deep_translator import GoogleTranslator

def detect_and_translate(text: str) -> dict:
    """
    Detects the language of the complaint and translates it to English.
    
    Why do we need this?
    Citizens in Tamil Nadu might write in Tamil, those in UP in Hindi etc.
    The system needs everything in English to process it consistently.
    
    deep-translator uses Google Translate internally but is completely free
    and needs no API key — it works like a browser would.
    
    Returns:
    - original_text: what the citizen typed
    - translated_text: English version
    - detected_language: what language it was in
    """
    try:
        # 'auto' tells the translator to detect language automatically
        translated = GoogleTranslator(source='auto', target='english').translate(text)
        
        # Detect source language separately
        detected = GoogleTranslator(source='auto', target='english')
        detected.translate(text)
        source_lang = detected.source
        
        return {
            "original_text": text,
            "translated_text": translated,
            "detected_language": source_lang
        }
    except Exception as e:
        print(f"[Translator] Error: {e}")
        return {
            "original_text": text,
            "translated_text": text,  # fallback — use original
            "detected_language": "unknown"
        }