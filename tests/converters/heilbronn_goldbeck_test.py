"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from pathlib import Path
from unittest.mock import Mock

import pytest
from requests_mock import Mocker

from parkapi_sources.converters import HeilbronnGoldbeckPullConverter
from parkapi_sources.util import RequestHelper
from tests.converters.helper import (
    validate_realtime_parking_site_inputs,
    validate_static_parking_site_inputs,
)


@pytest.fixture
def heilbronn_goldbeck_config_helper(mocked_config_helper: Mock):
    config = {
        'PARK_API_HEILBRONN_GOLDBECK_USERNAME': 'user',
        'PARK_API_HEILBRONN_GOLDBECK_PASSWORD': 'pass',
    }
    mocked_config_helper.get.side_effect = lambda key, default=None: config.get(key, default)
    return mocked_config_helper


@pytest.fixture
def heilbronn_goldbeck_pull_converter(
    heilbronn_goldbeck_config_helper: Mock, request_helper: RequestHelper
) -> HeilbronnGoldbeckPullConverter:
    return HeilbronnGoldbeckPullConverter(config_helper=heilbronn_goldbeck_config_helper, request_helper=request_helper)


class HeilbronnGoldbeckPullConverterTest:
    @staticmethod
    def test_get_static_parking_sites(
        heilbronn_goldbeck_pull_converter: HeilbronnGoldbeckPullConverter, requests_mock: Mocker
    ):
        json_path = Path(Path(__file__).parent, 'data', 'heilbronn_goldbeck_facilities.json')
        with json_path.open() as json_file:
            json_data_facilities = json_file.read()

        requests_mock.get(
            'https://control.goldbeck-parking.de/ipaw/services/v4x0/facilities?address=true&position=true&tariffs=true',
            text=json_data_facilities,
        )

        json_path = Path(Path(__file__).parent, 'data', 'heilbronn_goldbeck_occupancies.json')
        with json_path.open() as json_file:
            json_data_occupancies = json_file.read()
        requests_mock.get(
            'https://control.goldbeck-parking.de/ipaw/services/v4x0/occupancies',
            text=json_data_occupancies,
        )
        static_parking_site_inputs, import_parking_site_exceptions = (
            heilbronn_goldbeck_pull_converter.get_static_parking_sites()
        )

        assert len(static_parking_site_inputs) == 9
        assert len(import_parking_site_exceptions) == 1

        validate_static_parking_site_inputs(static_parking_site_inputs)

    @staticmethod
    def test_get_realtime_parking_sites(
        heilbronn_goldbeck_pull_converter: HeilbronnGoldbeckPullConverter, requests_mock: Mocker
    ):
        json_path = Path(Path(__file__).parent, 'data', 'heilbronn_goldbeck_occupancies.json')
        with json_path.open() as json_file:
            json_data = json_file.read()

        requests_mock.get(
            'https://control.goldbeck-parking.de/ipaw/services/v4x0/occupancies',
            text=json_data,
        )
        realtime_parking_site_inputs, import_parking_site_exceptions = (
            heilbronn_goldbeck_pull_converter.get_realtime_parking_sites()
        )

        assert len(realtime_parking_site_inputs) == 9
        assert len(import_parking_site_exceptions) == 1

        validate_realtime_parking_site_inputs(realtime_parking_site_inputs)
