"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from opening_hours import OpeningHours
from opening_hours.opening_hours import ParserError
from validataclass.exceptions import ValidationError
from validataclass.validators import StringValidator


class InvalidOpeningTimesError(ValidationError):
    code = 'invalid_opening_times'


class OsmOpeningTimesValidator(StringValidator):
    def validate(self, input_data: str, **kwargs) -> str:
        input_data = super().validate(input_data, **kwargs)

        try:
            OpeningHours(input_data)
        except ParserError as e:
            raise InvalidOpeningTimesError(reason='Invalid OSM opening time') from e

        return input_data
