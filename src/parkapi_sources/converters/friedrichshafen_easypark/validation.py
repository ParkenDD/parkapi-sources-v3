"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from typing import Any

from validataclass.validators import EnumValidator


class StrippedEnumValidator(EnumValidator):
    """
    Variant of `EnumValidator` which strips surrounding whitespace from string input before validating it, as the
    source data contains values with trailing whitespace.
    """

    def validate(self, input_data: Any, **kwargs: Any) -> Any:
        if isinstance(input_data, str):
            input_data = input_data.strip()

        return super().validate(input_data, **kwargs)
