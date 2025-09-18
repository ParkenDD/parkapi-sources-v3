"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from typing import Any

from validataclass.validators import ListValidator


class CommaSeparatedListValidator(ListValidator):
    def validate(self, input_data: Any, **kwargs) -> list:
        self._ensure_type(input_data, str)

        input_data = input_data.split(',')
        input_data = [item.strip() for item in input_data]

        return super().validate(input_data, **kwargs)
