"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from enum import Enum
from typing import Any

import pytest
from validataclass.exceptions import ValidationError

from parkapi_sources.validators import NoneableEnumValidator


class ExampleEnum(Enum):
    FOO = 'foo'
    BAR = 'bar'
    NUMBER = 3


@pytest.mark.parametrize(
    'input_data,output_data',
    [
        ('foo', ExampleEnum.FOO),
        ('bar', ExampleEnum.BAR),
        # EnumValidator matches strings case-insensitively by default
        ('FOO', ExampleEnum.FOO),
        (3, ExampleEnum.NUMBER),
    ],
)
def test_noneable_enum_validator_known_value(input_data: Any, output_data: ExampleEnum):
    validator = NoneableEnumValidator(ExampleEnum)

    assert validator.validate(input_data) is output_data


@pytest.mark.parametrize(
    'input_data',
    [
        'baz',
        'unknown',
        '',
        99,
    ],
)
def test_noneable_enum_validator_unknown_value_returns_none(input_data: Any):
    validator = NoneableEnumValidator(ExampleEnum)

    assert validator.validate(input_data) is None


@pytest.mark.parametrize(
    'input_data',
    [
        None,
        ['foo'],
        {'foo': 'bar'},
    ],
)
def test_noneable_enum_validator_invalid_type_still_fails(input_data: Any):
    validator = NoneableEnumValidator(ExampleEnum)

    with pytest.raises(ValidationError):
        validator.validate(input_data)
