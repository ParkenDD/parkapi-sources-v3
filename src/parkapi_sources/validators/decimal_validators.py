"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from decimal import Decimal
from typing import Any

from validataclass.validators import DecimalValidator


class GermanDecimalValidator(DecimalValidator):
    def validate(self, input_data: Any, **kwargs) -> Decimal:
        self._ensure_type(input_data, str)

        input_data = input_data.replace(',', '.')

        return super().validate(input_data, **kwargs)
