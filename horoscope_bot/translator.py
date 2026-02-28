import logging
from deep_translator import GoogleTranslator

logger = logging.getLogger(__name__)

def translate_to_telugu(text: str) -> str:
    """
    Translates the given English text to Telugu using deep-translator.
    """
    try:
        # deep-translator handles empty/short strings gracefully, often returning the input
        # or an empty string, so the explicit check might not be strictly necessary
        # but can be kept if specific behavior is desired.
        # For now, following the provided new code structure.
        
        translator = GoogleTranslator(source='en', target='te')
        return translator.translate(text)
    except Exception as e:
        logger.error(f"Translation Error: {e}")
        return text # Fallback to original text on failure
