"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import time

import pytest

from parkapi_sources.validators import ExcelTimeValidator


@pytest.mark.parametrize(
    'input_data,output_data',
    [
        ('12:30:00', time(12, 30)),
        (time(12, 30), time(12, 30)),
    ],
)
def test_excel_time_validator_success(input_data: str | time, output_data: time):
    validator = ExcelTimeValidator()

    assert validator.validate(input_data) == output_data
