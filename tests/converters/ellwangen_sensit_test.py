"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from pathlib import Path
from unittest.mock import Mock

import pytest
from requests_mock import Mocker

from parkapi_sources.converters import EllwangenSensitPullConverter
from parkapi_sources.util import RequestHelper
from tests.converters.helper import (
    validate_realtime_parking_site_inputs,
    validate_static_parking_site_inputs,
)


@pytest.fixture
def ellwangen_sensit_config_helper(mocked_config_helper: Mock):
    config = {
        'PARK_API_ELLWANGEN_SENSIT_USER': 'user',
        'PARK_API_ELLWANGEN_SENSIT_PASSWORD': 'pass',
    }
    mocked_config_helper.get.side_effect = lambda key, default=None: config.get(key, default)
    return mocked_config_helper


@pytest.fixture
def ellwangen_sensit_pull_converter(
    ellwangen_sensit_config_helper: Mock, request_helper: RequestHelper
) -> EllwangenSensitPullConverter:
    return EllwangenSensitPullConverter(config_helper=ellwangen_sensit_config_helper, request_helper=request_helper)


class EllwangenSensitPullConverterTest:
    @staticmethod
    def test_get_static_parking_sites(
        ellwangen_sensit_pull_converter: EllwangenSensitPullConverter,
        requests_mock: Mocker,
    ):
        json_path = Path(Path(__file__).parent, 'data', 'ellwangen_sensit.json')
        with json_path.open() as json_file:
            json_data = json_file.read()

        requests_mock.get(
            'https://ellwangen.nedapparking.com/api/v1/parkingLots',
            text=json_data,
        )

        static_parking_site_inputs, import_parking_site_exceptions = (
            ellwangen_sensit_pull_converter.get_static_parking_sites()
        )

        assert len(static_parking_site_inputs) == 1
        assert len(import_parking_site_exceptions) == 0

        validate_static_parking_site_inputs(static_parking_site_inputs)

    @staticmethod
    def test_get_realtime_parking_sites(
        ellwangen_sensit_pull_converter: EllwangenSensitPullConverter,
        requests_mock: Mocker,
    ):
        json_path = Path(Path(__file__).parent, 'data', 'ellwangen_sensit.json')
        with json_path.open() as json_file:
            json_data = json_file.read()

        requests_mock.get(
            'https://ellwangen.nedapparking.com/api/v1/parkingLots',
            text=json_data,
        )

        realtime_parking_site_inputs, import_parking_site_exceptions = (
            ellwangen_sensit_pull_converter.get_realtime_parking_sites()
        )

        assert len(realtime_parking_site_inputs) == 1
        assert len(import_parking_site_exceptions) == 0

        validate_realtime_parking_site_inputs(realtime_parking_site_inputs)
