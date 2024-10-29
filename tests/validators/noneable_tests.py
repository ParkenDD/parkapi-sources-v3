"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from decimal import Decimal
from typing import Any, Optional

import pytest
from validataclass.exceptions import ValidationError
from validataclass.helpers import UnsetValue
from validataclass.validators import StringValidator

from parkapi_sources.validators import ExcelNoneable


@pytest.mark.parametrize(
    'input_data,output_data',
    [
        ('', None),
        ('-', None),
        (None, None),
        ('cookies', 'cookies'),
    ],
)
def test_excel_noneable_success(input_data: Any, output_data: Optional[str]):
    validator = ExcelNoneable(StringValidator())

    validates_output_data = validator.validate(input_data)

    if output_data is None:
        assert validates_output_data is output_data
    else:
        assert validates_output_data == output_data


@pytest.mark.parametrize(
    'input_data',
    [
        1,
        Decimal('3'),
        UnsetValue,
    ],
)
def test_excel_noneable_fail(input_data: Any):
    validator = ExcelNoneable(StringValidator())

    with pytest.raises(ValidationError):
        validator.validate(input_data)
