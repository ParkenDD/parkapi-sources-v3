"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from decimal import ROUND_HALF_UP, Decimal


def round_7d(value: Decimal | float) -> Decimal:
    if isinstance(value, float):
        value = Decimal(str(value))
    return value.quantize(Decimal('1.0000000'), rounding=ROUND_HALF_UP)
