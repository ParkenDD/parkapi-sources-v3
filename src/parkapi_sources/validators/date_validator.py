"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import date, datetime
from typing import Any

from validataclass.exceptions import ValidationError
from validataclass.validators import StringValidator


class ParsedDateValidator(StringValidator):
    date_formats: list[str]

    def __init__(self, *args, date_format: str | list[str], **kwargs):
        super().__init__(*args, **kwargs)
        self.date_formats = [date_format] if isinstance(date_format, str) else date_format

    def validate(self, input_data: Any, **kwargs) -> date:
        input_data = super().validate(input_data, **kwargs)

        for date_format in self.date_formats:
            try:
                return datetime.strptime(input_data, date_format).date()
            except ValueError:
                continue

        raise ValidationError(
            code='invalid_date',
            reason=f'{input_data} does not have required date format {", ".join(self.date_formats)}.',
        )
