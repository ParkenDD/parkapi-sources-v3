"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from typing import Any

from isodate import Duration, ISO8601Error, parse_duration
from validataclass.exceptions import ValidationError
from validataclass.validators import StringValidator


class InvalidIsoDurationError(ValidationError):
    code = 'invalid_iso_duration'


class IsoDurationValidator(StringValidator):
    """
    Validator for ISO durations. We don't use Python timedelta because it does not support month / year.
    """

    def validate(self, input_data: Any, **kwargs: Any) -> Duration:
        input_data = super().validate(input_data, **kwargs)
        try:
            return parse_duration(input_data)
        except ISO8601Error as e:
            raise InvalidIsoDurationError from e
