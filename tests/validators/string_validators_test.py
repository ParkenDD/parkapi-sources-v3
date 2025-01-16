"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from typing import Any

import pytest

from parkapi_sources.validators import NumberCastingStringValidator


@pytest.mark.parametrize(
    'input_data,output_data',
    [
        (1, '1'),
        (1.2, '1.2'),
        ('cookies', 'cookies'),
    ],
)
def test_number_casting_string_validator_success(input_data: Any, output_data: str):
    validator = NumberCastingStringValidator()

    assert validator.validate(input_data) == output_data
