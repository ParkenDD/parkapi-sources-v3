"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from pathlib import Path
from unittest.mock import Mock

import pytest
from requests_mock import Mocker

from parkapi_sources.converters import FriedrichshafenSensorsPullConverter
from parkapi_sources.util import RequestHelper
from tests.converters.helper import validate_realtime_parking_spot_inputs, validate_static_parking_spot_inputs


@pytest.fixture
def friedrichshafen_sensors_config_helper(mocked_config_helper: Mock):
    config = {
        'PARK_API_MOBILITHEK_CERT': '/dev/null',
        'PARK_API_MOBILITHEK_KEY': '/dev/null',
        'PARK_API_MOBILITHEK_FRIEDRICHSHAFEN_SENSORS_STATIC_SUBSCRIPTION_ID': 1234567890,
        'PARK_API_MOBILITHEK_FRIEDRICHSHAFEN_SENSORS_REALTIME_SUBSCRIPTION_ID': 1234567890,
    }
    mocked_config_helper.get.side_effect = lambda key, default=None: config.get(key, default)
    return mocked_config_helper


@pytest.fixture
def friedrichshafen_sensors_pull_converter(
    friedrichshafen_sensors_config_helper: Mock, request_helper: RequestHelper
) -> FriedrichshafenSensorsPullConverter:
    return FriedrichshafenSensorsPullConverter(
        config_helper=friedrichshafen_sensors_config_helper, request_helper=request_helper
    )


class FriedrichshafenSensorsConverterTest:
    @staticmethod
    def test_get_static_parking_spots(
        friedrichshafen_sensors_pull_converter: FriedrichshafenSensorsPullConverter,
        requests_mock: Mocker,
    ):
        xml_path = Path(Path(__file__).parent, 'data', 'friedrichshafen-sensors-static.xml')
        with xml_path.open() as xml_file:
            xml_data = xml_file.read()

        requests_mock.get(
            'https://mobilithek.info:8443/mobilithek/api/v1.0/subscription/1234567890/clientPullService?subscriptionID=1234567890',
            text=xml_data,
        )

        static_parking_spot_inputs, import_parking_spot_exceptions = (
            friedrichshafen_sensors_pull_converter.get_static_parking_spots()
        )

        assert len(static_parking_spot_inputs) == 55
        assert len(import_parking_spot_exceptions) == 0

        validate_static_parking_spot_inputs(static_parking_spot_inputs)

    @staticmethod
    def test_get_realtime_parking_spots(
        friedrichshafen_sensors_pull_converter: FriedrichshafenSensorsPullConverter,
        requests_mock: Mocker,
    ):
        xml_path = Path(Path(__file__).parent, 'data', 'friedrichshafen-sensors-realtime.xml')
        with xml_path.open() as xml_file:
            xml_data = xml_file.read()

        requests_mock.get(
            'https://mobilithek.info:8443/mobilithek/api/v1.0/subscription/1234567890/clientPullService?subscriptionID=1234567890',
            text=xml_data,
        )

        realtime_parking_spot_inputs, import_parking_spot_exceptions = (
            friedrichshafen_sensors_pull_converter.get_realtime_parking_spots()
        )

        assert len(realtime_parking_spot_inputs) == 55
        assert len(import_parking_spot_exceptions) == 0

        validate_realtime_parking_spot_inputs(realtime_parking_spot_inputs)
