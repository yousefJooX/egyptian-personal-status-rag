import re

TASHKEEL = re.compile(r"[\u064B-\u0652\u0670]")       
ALEF_FORMS = re.compile(r"[أإآٱ]")
ARABIC_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")


def normalize_ar(text: str) -> str:
    """Unify Arabic spelling variants before search (never for display)."""
    text = TASHKEEL.sub("", text)        
    text = text.replace("\u0640", "")    
    text = ALEF_FORMS.sub("ا", text)    
    text = text.translate(ARABIC_DIGITS) 
    return text