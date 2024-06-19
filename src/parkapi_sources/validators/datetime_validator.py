"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Any

from validataclass.exceptions import ValidationError
from validataclass.validators import DateTimeValidator, IntegerValidator, StringValidator


class Rfc1123DateTimeValidator(StringValidator):
    def validate(self, input_data: Any, **kwargs) -> datetime:
        input_data = super().validate(input_data, **kwargs)

        try:
            input_data = parsedate_to_datetime(input_data)
            return input_data.astimezone(tz=timezone.utc)
        except ValueError as e:
            raise ValidationError(reason='Invalid RFD 1123 datetime') from e


class SpacedDateTimeValidator(DateTimeValidator):
    def validate(self, input_data: Any, **kwargs) -> datetime:
        self._ensure_type(input_data, str)

        if len(input_data) > 10 and input_data[10] == ' ':
            input_data = f'{input_data[:10]}T{input_data[11:]}'

        return super().validate(input_data, **kwargs)


class TimestampDateTimeValidator(IntegerValidator):
    divisor: int

    def __init__(self, *args, divisor: int = 1, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.divisor = divisor
        self.min_value = self.min_value * divisor
        self.max_value = self.max_value * divisor

    def validate(self, input_data: Any, **kwargs) -> datetime:
        input_data = super().validate(input_data, **kwargs)

        if self.divisor != 1:
            input_data = input_data / self.divisor

        try:
            return datetime.fromtimestamp(input_data, tz=timezone.utc)
        except ValueError as e:
            raise ValidationError(reason='Invalid timestamp') from e
