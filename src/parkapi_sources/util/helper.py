"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import re
import unicodedata
from decimal import ROUND_HALF_UP, Decimal


def round_7d(value: Decimal | float) -> Decimal:
    if isinstance(value, float):
        value = Decimal(str(value))
    return value.quantize(Decimal('1.0000000'), rounding=ROUND_HALF_UP)


def slugify(value: str) -> str:
    """
    Generates a stable, ASCII-only identifier from a name, e.g. 'Parkhaus Nürnberger Straße' becomes
    'parkhaus-nuernberger-strasse'. Used for sources which do not provide IDs.
    """
    value = value.lower()
    for search, replace in (('ä', 'ae'), ('ö', 'oe'), ('ü', 'ue'), ('ß', 'ss')):
        value = value.replace(search, replace)
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    return re.sub(r'[^a-z0-9]+', '-', value).strip('-')
