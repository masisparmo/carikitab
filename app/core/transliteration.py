import re
from rapidfuzz import process, fuzz

# Custom mapping dictionary for common words and book titles
INDO_TO_ARAB_DICT = {
    # Authors and common names
    "bukhari": "البخاري",
    "muslim": "مسلم",
    "tirmidzi": "الترمذي",
    "abu dawud": "أبو داود",
    "nasai": "النسائي",
    "ibnu majah": "ابن ماجه",
    "nawawi": "النووي",
    "ibnu taimiyah": "ابن تيمية",
    "ibnu qayyim": "ابن القيم",
    "ibnu hajar": "ابن حجر",
    "asy-syafi'i": "الشافعي",
    "syafi'i": "الشافعي",
    "ahmad": "أحمد",
    "malik": "مالك",
    "abu hanifah": "أبو حنيفة",
    "albani": "الألباني",
    "bin baz": "ابن باز",
    "utsaimin": "العثيمين",
    "fauzan": "الفوزان",
    "suyuthi": "السيوطي",
    "dzahabi": "الذهبي",
    "katsir": "كثير",
    "ibnu katsir": "ابن كثير",
    "qurtubi": "القرطبي",
    "thabari": "الطبري",

    # Common standalone words (CRITICAL for multi-word queries)
    "ibnu": "ابن",
    "bin": "بن",
    "binti": "بنت",
    "abu": "أبو",
    "ummu": "أم",
    "ali": "علي",
    "umar": "عمر",
    "utsman": "عثمان",
    "aisyah": "عائشة",
    "fatimah": "فاطمة",

    # Book Titles and Categories
    "siyar a'lam an nubala": "سير أعلام النبلاء",
    "siyar a'lam an-nubala": "سير أعلام النبلاء",
    "siyar": "سير",
    "a'lam": "أعلام",
    "nubala": "النبلاء",
    "al itqan": "الإتقان",
    "itqan": "الإتقان",
    "fathul bari": "فتح الباري",
    "fathul baari": "فتح الباري",
    "syarah muslim": "شرح صحيح مسلم",
    "shahih bukhari": "صحيح البخاري",
    "shahih muslim": "صحيح مسلم",
    "riyadhus shalihin": "رياض الصالحين",
    "bulughul maram": "بلغ المرام",
    "umdatul ahkam": "عمدة الأحكام",
    "al-muwaththa": "الموطأ",
    "lathaiful ma'arif": "لطائف المعارف",
    "subulus salam": "سبل السلام",
    "nailul authar": "نيل الأوطار",
    "zaadul ma'ad": "زاد المعاد",

    # General keywords
    "shahih": "صحيح",
    "sunan": "سنن",
    "musnad": "مسند",
    "tafsir": "تفسير",
    "syarah": "شرح",
    "matan": "متن",
    "majmu": "مجموع",
    "minhaj": "منهاج",
    "risalah": "رسالة",
    "kitab": "كتاب",
    "aqidah": "عقيدة",
    "tauhid": "توحيد",
    "fiqh": "فقه",
    "ushul": "أصول",
    "hadits": "حديث",
    "tashawwuf": "تصوف",
    "tarikh": "تاريخ",
    "sirah": "سيرة",
    "nabawiyah": "نبوية",
    "muwaththa": "موطأ",
    "muwaththa'": "موطأ",
    "quran": "قرآن",
    "qur'an": "قرآن",
    "islami": "إسلامي",
    "fiqh": "فقه",

    # Common words and names missing from typical searches
    "syamail": "الشمائل",
    "asy-syamail": "الشمائل",
    "syamail muhammadiyah": "الشمائل المحمدية",
    "muhammad": "محمد",
    "muhammadiyah": "المحمدية",
    "jawzi": "الجوزي",
    "ibnu jawzi": "ابن الجوزي",
    "ibn jawzi": "ابن الجوزي",
    "mawdhu'at": "الموضوعات",
    "al-mawdhu'at": "الموضوعات",
    "bajuri": "الباجوري",
    "al-bajuri": "الباجوري",
    "tirmidzi": "الترمذي",
    "at-tirmidzi": "الترمذي",
    "ghazali": "الغزالي",
    "al-ghazali": "الغزالي",
    "ihya ulumiddin": "إحياء علوم الدين",
    "ihya": "إحياء",
    "razi": "الرازي",
    "jalalain": "الجلالين",
    "nabi": "النبي",
    "rasulullah": "رسول الله",
    "shalat": "صلاة",
    "shalawat": "صلوات",
    "doa": "دعاء",
    "dzikir": "ذكر",
    "ibnul": "ابن",
    "imam": "إمام",
    "syaikh": "شيخ",
    "ulum": "علوم",
    "ulama": "علماء",
    # Hanbali, Maliki, etc..
    "hanbali": "الحنبلي",
    "hanafi": "الحنفي",
    "maliki": "المالكي",
    "syafii": "الشافعي",
}

# Reverse mapping for Arabic to Latin transliteration
ARAB_TO_INDO_DICT = {v: k.title() for k, v in INDO_TO_ARAB_DICT.items()}

# Basic Character Transliteration Map for fallback
ARABIC_TO_LATIN_CHARS = {
    'ا': 'a', 'أ': 'a', 'إ': 'i', 'آ': 'aa', 'ب': 'b', 'ت': 't', 'ث': 'ts',
    'ج': 'j', 'ح': 'h', 'خ': 'kh', 'د': 'd', 'ذ': 'dz', 'ر': 'r', 'ز': 'z',
    'س': 's', 'ش': 'sy', 'ص': 'sh', 'ض': 'dh', 'ط': 'th', 'ظ': 'zh', 'ع': "'",
    'غ': 'gh', 'ف': 'f', 'ق': 'q', 'ك': 'k', 'ل': 'l', 'م': 'm', 'ن': 'n',
    'ه': 'h', 'و': 'w', 'ي': 'y', 'ى': 'a', 'ة': 't', 'ؤ': 'u', 'ئ': 'i',
    'ال': 'al-', ' ': ' ', '-': '-'
}

def is_arabic(text: str) -> bool:
    """Check if the text contains Arabic characters."""
    arabic_pattern = re.compile(r'[\u0600-\u06FF]')
    return bool(arabic_pattern.search(text))

def transliterate_to_arabic(query: str) -> str:
    """
    Translates an Indonesian query to Arabic using a predefined dictionary
    and fuzzy matching. If the text is already Arabic, returns it as is.
    Uses a longest-match-first strategy for multi-word phrases.
    """
    if not query:
        return ""
        
    if is_arabic(query):
        return query
        
    query_lower = query.lower().strip()
    words = query_lower.split()
    if not words:
        return ""

    result_words = []
    i = 0
    dict_keys = list(INDO_TO_ARAB_DICT.keys())

    while i < len(words):
        found_match = False
        # Try matching phrases from longest (max 4 words) to shortest (1 word)
        for length in range(min(4, len(words) - i), 0, -1):
            phrase = " ".join(words[i : i + length])
            
            # 1. Exact match for phrase
            if phrase in INDO_TO_ARAB_DICT:
                result_words.append(INDO_TO_ARAB_DICT[phrase])
                i += length
                found_match = True
                break
            
            # 2. Fuzzy match for phrase (only for single words or very specific lengths to avoid noise)
            if length == 1:
                match = process.extractOne(phrase, dict_keys, scorer=fuzz.ratio)
                if match and match[1] >= 90: # Higher threshold for single word fuzzy
                    result_words.append(INDO_TO_ARAB_DICT[match[0]])
                    i += length
                    found_match = True
                    break

        if not found_match:
            # Keep original word if no match found
            result_words.append(words[i])
            i += 1
                
    return " ".join(result_words)

def transliterate_to_latin(arabic_text: str) -> str:
    """
    Translates Arabic text to Latin offline using reverse dictionary mapping 
    and character-by-character mapping as a last resort.
    """
    if not arabic_text or not is_arabic(arabic_text):
        return arabic_text
        
    # 1. Check Exact Match in Dictionary
    for arab_k, latin_v in ARAB_TO_INDO_DICT.items():
        if arabic_text.strip() == arab_k:
            return latin_v
            
    # 2. Tokenize and replace known full words longest to shortest
    words = arabic_text.strip().split()
    result_words = []
    i = 0
    while i < len(words):
        found_match = False
        # Try matching phrases max 4 words
        for length in range(min(4, len(words) - i), 0, -1):
            phrase = " ".join(words[i : i + length])
            if phrase in ARAB_TO_INDO_DICT:
                result_words.append(ARAB_TO_INDO_DICT[phrase])
                i += length
                found_match = True
                break
        
        if not found_match:
            # Fallback to local character mapping
            token = words[i]
            # Replace 'ال' prefix manually first to handle al-
            if token.startswith('ال'):
                token = token[2:]
                mapped_token = 'Al-' + ''.join(ARABIC_TO_LATIN_CHARS.get(c, '') for c in token)
            elif token.startswith('وال'):
                token = token[3:]
                mapped_token = 'wa Al-' + ''.join(ARABIC_TO_LATIN_CHARS.get(c, '') for c in token)
            else:
                mapped_token = ''.join(ARABIC_TO_LATIN_CHARS.get(c, '') for c in token)
            
            result_words.append(mapped_token.title())
            i += 1
            
    # Clean up double spaces or weird artifacts
    final_str = " ".join(result_words)
    final_str = re.sub(r'\s+', ' ', final_str)
    return final_str.strip()

# For testing
if __name__ == "__main__":
    tests = [
        "Siyar a'lam an nubala",
        "Al itqan",
        "bukhari",
        "shahih muslim",
        "tafsir ibnu katsir",
        "sejarah", # Not in dict
        "سير أعلام النبلاء" # Already Arabic
    ]
    for t in tests:
        print(f"{t} -> {transliterate_to_arabic(t)}")
