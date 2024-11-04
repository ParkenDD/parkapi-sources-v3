"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import date
from typing import Any

import pytest
from validataclass.exceptions import ValidationError

from parkapi_sources.validators import ParsedDateValidator


@pytest.mark.parametrize(
    'date_format,input_data,output_data',
    [
        ('%d.%m.%Y', '01.02.2024', date(2024, 2, 1)),
        ('%m/%d/%Y', '02/01/2024', date(2024, 2, 1)),
    ],
)
def test_parsed_date_validator_success(date_format: str, input_data: Any, output_data: date):
    validator = ParsedDateValidator(date_format=date_format)

    assert validator.validate(input_data) == output_data


@pytest.mark.parametrize(
    'date_format,input_data',
    [
        ('%d.%m.%Y', '01/02/2024'),
        ('%d.%m.%Y', 20240201),
    ],
)
def test_parsed_date_validator_fail(date_format: str, input_data: Any):
    validator = ParsedDateValidator(date_format=date_format)

    with pytest.raises(ValidationError):
        validator.validate(input_data)
