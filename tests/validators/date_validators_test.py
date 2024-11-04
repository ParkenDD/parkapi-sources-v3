"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from typing import Any

import pytest
from validataclass.exceptions import ValidationError

from parkapi_sources.validators import GermanDurationIntegerValidator


@pytest.mark.parametrize(
    'input_data,output_data',
    [
        ('1 Stunde', 60 * 60),
        ('1 Stunden', 60 * 60),
        ('30 Stunden', 60 * 60 * 30),
        ('2 Quartale', 60 * 60 * 24 * 30 * 3 * 2),
    ],
)
def test_parsed_date_validator_success(input_data: Any, output_data: int):
    validator = GermanDurationIntegerValidator()

    assert validator.validate(input_data) == output_data


@pytest.mark.parametrize(
    'input_data',
    [
        '1 Cookie',
        '1 Stunden, 30 Minuten',
        ('30  Stunden', 60 * 60 * 30),
        '30_Stunden',
    ],
)
def test_parsed_date_validator_fail(input_data: Any):
    validator = GermanDurationIntegerValidator()

    with pytest.raises(ValidationError):
        validator.validate(input_data)
