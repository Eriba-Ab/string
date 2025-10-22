import hashlib
from collections import Counter
import re

def analyze_string(value: str):
    value_stripped = value.strip()
    sha_hash = hashlib.sha256(value_stripped.encode()).hexdigest()
    length = len(value_stripped)
    is_palindrome = value_stripped.lower() == value_stripped[::-1].lower()
    unique_chars = len(set(value_stripped))
    word_count = len(value_stripped.split())
    char_freq = dict(Counter(value_stripped))


    return {
        'length': length,
        'is_palindrome': is_palindrome,
        'unique_characters': unique_chars,
        'word_count': word_count,
        'sha256_hash': sha_hash,
        'character_frequency_map': char_freq
    }


def parse_natural_language_query(query: str):
    q = query.lower()
    filters = {}
    if 'palindromic' in q or 'palindrome' in q:
        filters['is_palindrome'] = True
    if 'single word' in q or 'one word' in q:
        filters['word_count'] = 1
    if 'longer than' in q:
        try:
            num = int(q.split('longer than')[1].split('character')[0].strip())
            filters['min_length'] = num + 1
        except:
            pass
    if 'containing the letter' in q or 'contains the letter' in q:
        letter = q.split('letter')[-1].strip().split()[0]
        filters['contains_character'] = letter
    elif 'contain' in q and len(q.split('contain')[-1].strip()) == 1:
        filters['contains_character'] = q.split('contain')[-1].strip()
    return filters