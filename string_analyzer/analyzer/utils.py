import re


def parse_nl_query(q: str):
q = q.lower().strip()
filters = {}
if 'single word' in q:
filters['word_count'] = 1
if 'palindromic' in q or 'palindrome' in q:
filters['is_palindrome'] = True
m = re.search(r'longer than (\d+)', q)
if m:
filters['min_length'] = int(m.group(1)) + 1
if 'containing the letter' in q:
m2 = re.search(r'letter ([a-z])', q)
if m2:
filters['contains_character'] = m2.group(1)
if 'first vowel' in q:
filters['contains_character'] = 'a'
if not filters:
raise ValueError('Unable to parse')
return filters