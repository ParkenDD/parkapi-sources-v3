"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from typing import Any

from validataclass.exceptions import ValueNotAllowedError
from validataclass.validators import EnumValidator


class NoneableEnumValidator(EnumValidator):
    """
    Variant of `EnumValidator` that returns None for values which are not part of the Enum, instead of raising a
    `ValueNotAllowedError`. This is useful for input data which may contain new, unknown enum values that should be
    ignored instead of failing the whole validation.
    """

    def validate(self, input_data: Any, **kwargs: Any) -> Any | None:
        try:
            return super().validate(input_data, **kwargs)
        except ValueNotAllowedError:
            return None
