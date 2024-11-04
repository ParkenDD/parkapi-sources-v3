"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from typing import Any

import pytest
from validataclass.exceptions import ValidationError

from parkapi_sources.validators import MappedBooleanValidator


@pytest.mark.parametrize(
    'mapping,input_data,output_data',
    [
        ({}, False, False),
        ({}, True, True),
        ({'true': True, 'false': False}, 'true', True),
        ({'true': True, 'false': False}, 'false', False),
        ({'true': True, 'false': False}, 'TRUE', True),
        ({1: True, 0: False}, 1, True),
    ],
)
def test_mapped_boolean_validator_success(mapping: dict, input_data: Any, output_data: bool):
    validator = MappedBooleanValidator(mapping=mapping)

    assert validator.validate(input_data) is output_data


@pytest.mark.parametrize(
    'mapping,input_data',
    [
        ({}, 'something'),
        ({'true': True, 'false': False}, 'something'),
        ({'true': True, 'false': False}, 1),
    ],
)
def test_mapped_boolean_validator_fail(mapping: dict, input_data: Any):
    validator = MappedBooleanValidator(mapping=mapping)

    with pytest.raises(ValidationError):
        validator.validate(input_data)
