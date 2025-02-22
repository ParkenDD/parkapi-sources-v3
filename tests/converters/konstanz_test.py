"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from pathlib import Path
from typing import Any
from unittest.mock import Mock

import pytest
from requests_mock import Mocker
from validataclass.exceptions import ValidationError

from parkapi_sources.converters import KonstanzPullConverter
from parkapi_sources.converters.konstanz.validators import (
    InvalidOpeningTimesError,
    KonstanzHeightValidator,
    KonstanzOpeningTimeValidator,
)
from parkapi_sources.util import RequestHelper
from tests.converters.helper import validate_realtime_parking_site_inputs, validate_static_parking_site_inputs


@pytest.fixture
def requests_mock_konstanz(requests_mock: Mocker) -> Mocker:
    json_path = Path(Path(__file__).parent, 'data', 'konstanz.json')
    with json_path.open() as json_file:
        json_data = json_file.read()

    requests_mock.get(
        'https://services.gis.konstanz.digital/geoportal/rest/services/Fachdaten/Parkplaetze_Parkleitsystem'
        '/MapServer/0/query?where=1%3D1&outFields=*&outSR=4326&f=json',
        text=json_data,
    )

    return requests_mock


@pytest.fixture
def konstanz_pull_converter(mocked_config_helper: Mock, request_helper: RequestHelper) -> KonstanzPullConverter:
    return KonstanzPullConverter(config_helper=mocked_config_helper, request_helper=request_helper)


class KonstanzPullConverterTest:
    @staticmethod
    def test_get_static_parking_sites(konstanz_pull_converter: KonstanzPullConverter, requests_mock_konstanz: Mocker):
        static_parking_site_inputs, import_parking_site_exceptions = konstanz_pull_converter.get_static_parking_sites()
        assert len(static_parking_site_inputs) == 11
        assert len(import_parking_site_exceptions) == 0

        validate_static_parking_site_inputs(static_parking_site_inputs)

    @staticmethod
    def test_get_realtime_parking_sites(konstanz_pull_converter: KonstanzPullConverter, requests_mock_konstanz: Mocker):
        realtime_parking_site_inputs, import_parking_site_exceptions = (
            konstanz_pull_converter.get_realtime_parking_sites()
        )

        assert len(realtime_parking_site_inputs) == 11
        assert len(import_parking_site_exceptions) == 0

        validate_realtime_parking_site_inputs(realtime_parking_site_inputs)


class KonstanzOpeningTimeValidatorTest:
    @staticmethod
    @pytest.mark.parametrize(
        'input_data,expected_result',
        [
            (
                'Mo-Fr:  07:00  -  01:30  Uhr\nSa:  07:00  -  01:30  Uhr\nSo:  08:00  -  00:30  Uhr',
                'Mo-Fr 07:00-01:30,Sa 07:00-01:30,Su 08:00-00:30',
            ),
            (
                'Mo-Fr:  06:00  -  23:00  Uhr\nSa:  06:00  -  23:00  Uhr\nSo: geschlossen',
                'Mo-Fr 06:00-23:00,Sa 06:00-23:00',
            ),
            (
                'ganztägig',
                '24/7',
            ),
        ],
    )
    def test_validate_success(input_data: str, expected_result: str):
        validator = KonstanzOpeningTimeValidator()
        assert validator.validate(input_data) == expected_result

    @staticmethod
    @pytest.mark.parametrize(
        'input_data',
        [
            'Mo-Fr:  07:00  -  01:30  Uhr\nSa:  07:00  -  01:30  Uhr\nSo:  08:00  -  00:30  Kekse',
            'Mo-Fr:  07:00  -  01:30  Uhr\nSa:  07:00  -  01:30  Uhr\nSo:  08:00  -  00:30  Uhr\nXy:  08:00  -  00:30  Uhr',
            'Mo-Fr:  07:00  -  01:30  Uhr\nSa:  07:00  -  01:30  Uhr\nSu:  08:00  -  00:30  Uhr',
        ],
    )
    def test_validate_fail(input_data: str):
        validator = KonstanzOpeningTimeValidator()
        with pytest.raises(InvalidOpeningTimesError):
            validator.validate(input_data)


class KonstanzHeightValidatorTest:
    @staticmethod
    @pytest.mark.parametrize(
        'input_data,expected_result',
        [
            ('2 m', 200),
            ('2,05 m', 205),
        ],
    )
    def test_validate_success(input_data: str, expected_result: int):
        validator = KonstanzHeightValidator()
        assert validator.validate(input_data) == expected_result

    @staticmethod
    @pytest.mark.parametrize(
        'input_data',
        [
            '200 cm',
            200,
            '2,05',
        ],
    )
    def test_validate_fail(input_data: Any):
        validator = KonstanzHeightValidator()
        with pytest.raises(ValidationError):
            validator.validate(input_data)
