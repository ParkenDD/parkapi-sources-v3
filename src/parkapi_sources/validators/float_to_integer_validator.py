"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from typing import Any

from validataclass.validators import IntegerValidator


class FloatToIntegerValidators(IntegerValidator):
    def validate(self, input_data: Any, **kwargs) -> int:
        if self.allow_strings and isinstance(input_data, str):
            input_data = float(input_data)

        if isinstance(input_data, float):
            input_data = int(input_data)

        return super().validate(input_data, **kwargs)
