"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import re
from decimal import Decimal
from typing import Any

from validataclass.exceptions import ValidationError
from validataclass.validators import DecimalValidator, IntegerValidator, StringValidator


class InvalidHeightError(ValidationError):
    code = 'invalid_height'


class KonstanzHeightValidator(DecimalValidator):
    def validate(self, input_data: Any, **kwargs) -> int:
        self._ensure_type(input_data, str)

        if not input_data.endswith(' m'):
            raise InvalidHeightError(reason=f'Invalid height: {input_data}')

        input_data = input_data[:-2].replace(',', '.')

        try:
            input_data = Decimal(input_data)
        except ValueError as e:
            raise InvalidHeightError(reason=f'Invalid height: {input_data}') from e

        return int(input_data * 100)


class InvalidOpeningTimesError(ValidationError):
    code = 'invalid_opening_times'


class KonstanzOpeningTimeValidator(StringValidator):
    opening_hours_pattern = re.compile(r'  (\d\d):(\d\d)  -  (\d\d):(\d\d)  Uhr')

    def validate(self, input_data: Any, **kwargs: Any) -> str:
        if input_data == 'ganztägig':
            return '24/7'

        splitted_input_data: list[str] = input_data.split('\n')
        if len(splitted_input_data) != 3:
            raise InvalidOpeningTimesError(reason=f'Invalid opening times {input_data}')

        if (
            not splitted_input_data[0].startswith('Mo-Fr:')
            or not splitted_input_data[1].startswith('Sa:')
            or not splitted_input_data[2].startswith('So:')
        ):
            raise InvalidOpeningTimesError(reason=f'Invalid opening times {input_data}')

        result_fragments = []
        for fragment in splitted_input_data:
            if fragment.endswith('geschlossen'):
                continue

            splitted_fragment = fragment.split(':', 1)

            opening_times = self.opening_hours_pattern.match(splitted_fragment[1])
            if not opening_times:
                raise InvalidOpeningTimesError(reason=f'Invalid opening times {input_data}')

            result_fragments.append(
                f'{splitted_fragment[0].replace("So", "Su")} '
                f'{opening_times.group(1)}:{opening_times.group(2)}-{opening_times.group(3)}:{opening_times.group(4)}',
            )

        return ','.join(result_fragments)


class NumericIntegerValidator(IntegerValidator):
    def validate(self, input_data: Any, **kwargs) -> int:
        self._ensure_type(input_data, [int, float])

        input_data = int(input_data)

        return super().validate(input_data, **kwargs)
