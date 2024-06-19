"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import json
import re
from json import JSONDecodeError
from typing import Any

from validataclass.exceptions import ValidationError
from validataclass.validators import ListValidator


class PointCoordinateTupleValidator(ListValidator):
    PATTERN = re.compile(r'POINT \(([-+]?\d+\.\d+) ([-+]?\d+\.\d+)\)')

    def validate(self, input_data: Any, **kwargs) -> list:
        self._ensure_type(input_data, str)
        input_match = re.match(self.PATTERN, input_data)

        if input_match is None:
            raise ValidationError(code='invalid_tuple_input', reason='invalid point coordinate tuple input')

        input_data = [input_match.group(1), input_match.group(2)]

        return super().validate(input_data, **kwargs)


class DumpedListValidator(ListValidator):
    def validate(self, input_data: Any, **kwargs) -> list:
        self._ensure_type(input_data, str)
        try:
            input_data = json.loads(input_data)
        except JSONDecodeError as e:
            raise ValidationError(code='invalid_json_input', reason=f'invalid JSON input: {e}') from e

        return super().validate(input_data, **kwargs)
