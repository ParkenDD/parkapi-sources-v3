"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timezone
from typing import Any

import pytest
from validataclass.exceptions import ValidationError

from parkapi_sources.validators import Rfc1123DateTimeValidator, SpacedDateTimeValidator, TimestampDateTimeValidator


@pytest.mark.parametrize(
    'input_data,output_data',
    [
        ('Sun Nov  6 08:49:37 2024', datetime(2024, 11, 6, 7, 49, 37, tzinfo=timezone.utc)),
        ('Sun, 06 Nov 2024 08:49:37 GMT', datetime(2024, 11, 6, 8, 49, 37, tzinfo=timezone.utc)),
        ('Sunday, 06-Nov-24 08:49:37 GMT', datetime(2024, 11, 6, 8, 49, 37, tzinfo=timezone.utc)),
        ('Sunday, 06-Nov-98 08:49:37 GMT', datetime(1998, 11, 6, 8, 49, 37, tzinfo=timezone.utc)),
        ('Sun Nov  6 08:49:37 2024', datetime(2024, 11, 6, 7, 49, 37, tzinfo=timezone.utc)),
    ],
)
def test_rfc1123_datetime_validator_success(input_data: str, output_data: datetime):
    validator = Rfc1123DateTimeValidator()

    assert validator.validate(input_data) == output_data


@pytest.mark.parametrize(
    'input_data',
    [
        1234567890,
        '',
        '2024-01-01T12:00:00',
    ],
)
def test_rfc1123_datetime_validator_fail(input_data: Any):
    validator = Rfc1123DateTimeValidator()

    with pytest.raises(ValidationError):
        validator.validate(input_data)


@pytest.mark.parametrize(
    'input_data,output_data',
    [
        ('2024-04-01 12:13:14', datetime(2024, 4, 1, 12, 13, 14)),
        ('2024-04-01T12:13:14', datetime(2024, 4, 1, 12, 13, 14)),
    ],
)
def test_spaced_datetime_validator_success(input_data: str, output_data: datetime):
    validator = SpacedDateTimeValidator()

    assert validator.validate(input_data) == output_data


@pytest.mark.parametrize(
    'input_data',
    [
        1234567890,
        '',
        '2024-01-01_12:00:00',
    ],
)
def test_spaced_datetime_validator_fail(input_data: Any):
    validator = SpacedDateTimeValidator()

    with pytest.raises(ValidationError):
        validator.validate(input_data)


@pytest.mark.parametrize(
    'input_data,divisor,output_data',
    [
        (1717922614, 1, datetime(2024, 6, 9, 8, 43, 34, tzinfo=timezone.utc)),
        (1717922614000, 1000, datetime(2024, 6, 9, 8, 43, 34, tzinfo=timezone.utc)),
    ],
)
def test_timestamp_datetime_validator_success(input_data: Any, divisor: int, output_data: datetime):
    validator = TimestampDateTimeValidator(divisor=divisor)

    assert validator.validate(input_data) == output_data


@pytest.mark.parametrize(
    'input_data',
    [
        '',
        '2024-01-01_12:00:00',
    ],
)
def test_timestamp_datetime_validator_fail(input_data: Any):
    validator = TimestampDateTimeValidator()

    with pytest.raises(ValidationError):
        validator.validate(input_data)
