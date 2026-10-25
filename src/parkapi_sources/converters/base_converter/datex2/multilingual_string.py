"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from typing import Any


def get_localised_text(multilingual_string: Any, lang: str = 'de') -> str | None:
    """
    Returns the text of a DATEX II v3 MultilingualString, flattened by XMLHelper with ('values', 'value') as
    conditional remote type tags. Depending on the number of values and the lang attribute, this is a string, a dict
    like {'lang': 'de', '_text': '...'} or a list of both. The value in the given language is preferred, otherwise
    the first value is used.
    """
    if multilingual_string is None:
        return None

    values = multilingual_string if isinstance(multilingual_string, list) else [multilingual_string]
    texts: list[tuple[str | None, str]] = []
    for value in values:
        if isinstance(value, str):
            texts.append((None, value))
        elif isinstance(value, dict) and value.get('_text'):
            texts.append((value.get('lang'), value['_text']))

    for text_lang, text in texts:
        if text_lang == lang:
            return text
    if texts:
        return texts[0][1]
    return None
