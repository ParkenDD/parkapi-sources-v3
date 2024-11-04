"""
Giro-e Backend
Copyright (c) 2024, binary butterfly GmbH
All rights reserved.
"""

import json
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Any

import pytest

from parkapi_sources.util.encoding import DefaultJSONEncoder, convert_to_serializable_value


class TestEnum(Enum):
    TEST = 'TEST'


@dataclass
class TestToDictClass:
    key: str

    def to_dict(self) -> dict:
        return {'key': self.key}


@dataclass
class TestDictClass:
    key: str


@pytest.mark.parametrize(
    'input_data,output_data',
    [
        (datetime(2024, 6, 1, 12), '2024-06-01T12:00:00Z'),
        (date(2024, 6, 1), '2024-06-01'),
        (Decimal('1.30'), '1.30'),
        (TestEnum.TEST, 'TEST'),
        (b'abcd', 'abcd'),
        (TestToDictClass(key='TEST'), {'key': 'TEST'}),
        (TestDictClass(key='TEST'), {'key': 'TEST'}),
        (1, '1'),
    ],
)
def test_convert_to_serializable_value(input_data: Any, output_data: str):
    assert convert_to_serializable_value(input_data) == output_data


@pytest.mark.parametrize(
    'input_data,output_data',
    [
        ({'test': 'something'}, '{"test": "something"}'),
        (
            {
                'test-datetime': datetime(2024, 10, 1, 12),
                'test-decimal': Decimal('1.33'),
            },
            '{"test-datetime": "2024-10-01T12:00:00Z", "test-decimal": "1.33"}',
        ),
        (
            [1, 2, 'cookies', {'test': 3}],
            '[1, 2, "cookies", {"test": 3}]',
        ),
    ],
)
def test_json_encoder(input_data: Any, output_data: str):
    assert json.dumps(input_data, cls=DefaultJSONEncoder) == output_data
