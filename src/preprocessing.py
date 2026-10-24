"""Lightweight text preprocessing helpers used by the BookWise experiments."""
import re
from collections import Counter

STOPWORDS = set('a an the and or is are was were be been being of to in for on with it this that as by from at into about after before but not no so if than then too very can could would should i you he she we they them his her our your their my me book books story stories novel novels'.split())


def tokenize(text):
    return re.findall(r"[A-Za-z]+(?:'[A-Za-z]+)?|\d+|[^\w\s]", str(text))


def filter_tokens(tokens):
    return [t for t in tokens if re.search(r'[A-Za-z0-9]', t) and t.lower() not in STOPWORDS]


def validate_script(text):
    scripts = Counter()
    for char in str(text):
        if char.isalpha():
            name = 'Latin' if 'LATIN' in __import__('unicodedata').name(char, '') else 'Other'
            scripts[name] += 1
    return {'valid': bool(scripts), 'scripts_found': dict(scripts), 'message': 'Latin text detected' if scripts.get('Latin') and not scripts.get('Other') else ('Mixed or non-Latin script detected' if scripts else 'No alphabetic characters detected')}


def _stem(word):
    w = word.lower()
    for suffix in ('ingly','edly','ation','ments','ment','ness','ing','ers','ies','ied','ed','ly','es','s'):
        if len(w) > len(suffix) + 3 and w.endswith(suffix):
            if suffix in ('ies','ied'):
                return w[:-len(suffix)] + 'y'
            return w[:-len(suffix)]
    return w


def _lemma(word):
    w = word.lower()
    irregular = {'children':'child','mice':'mouse','better':'good','best':'good','went':'go','written':'write','stories':'story','leaves':'leaf','running':'run'}
    if w in irregular: return irregular[w]
    if w.endswith('ies') and len(w)>4: return w[:-3]+'y'
    if w.endswith('ing') and len(w)>5: return w[:-3]
    if w.endswith('ed') and len(w)>4: return w[:-2]
    if w.endswith('s') and len(w)>3: return w[:-1]
    return w


def stopword_stem_lemma(text):
    tokens = [t for t in tokenize(text) if re.fullmatch(r'[A-Za-z]+', t)]
    filtered = [t for t in tokens if t.lower() not in STOPWORDS]
    return {'tokens': tokens, 'without_stopwords': filtered, 'stemmed': [_stem(t) for t in filtered], 'lemmatized': [_lemma(t) for t in filtered]}


def morphology(text):
    words = [t for t in tokenize(text) if re.fullmatch(r'[A-Za-z]+', t)]
    rows = []
    for word in words:
        w = word.lower()
        if w.endswith('ies'): root, form = w[:-3]+'y', 'plural/verb form'
        elif w.endswith('ing'): root, form = w[:-3], 'present participle'
        elif w.endswith('ed'): root, form = w[:-2], 'past tense'
        elif w.endswith('s') and len(w)>3: root, form = w[:-1], 'plural/third-person form'
        else: root, form = w, 'base form / not recognized'
        rows.append({'word': word, 'root_guess': root, 'morphology': form, 'generated_example': root+'s' if root != w else w+'s'})
    return {'analysis': rows}
