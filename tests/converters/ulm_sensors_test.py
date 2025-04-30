"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from pathlib import Path
from unittest.mock import Mock

import pytest
from requests_mock import Mocker

from parkapi_sources.converters import UlmSensorsPullConverter
from parkapi_sources.util import RequestHelper
from tests.converters.helper import (
    validate_realtime_parking_site_inputs,
    validate_realtime_parking_spot_inputs,
    validate_static_parking_site_inputs,
    validate_static_parking_spot_inputs,
)


@pytest.fixture
def ulm_sensors_config_helper(mocked_config_helper: Mock):
    config = {
        'PARK_API_ULM_SENSORS_USER': 'ffe455aa-7ca9-4281-b5c4-0c7561f9b514',
        'PARK_API_ULM_SENSORS_PASSWORD': 'ffe455aa-7ca9-4281-b5c4-0c7561f9b514',
        'PARK_API_ULM_SENSORS_CLIENT_ID': 'ffe455aa-7ca9-4281-b5c4-0c7561f9b514',
        'PARK_API_ULM_SENSORS_IDS': 'id1,id2,id3,id4,id5',
        'STATIC_GEOJSON_BASE_URL': 'https://raw.githubusercontent.com/ParkenDD/parkapi-static-data/main/sources',
    }
    mocked_config_helper.get.side_effect = lambda key, default=None: config.get(key, default)
    return mocked_config_helper


@pytest.fixture
def ulm_sensors_pull_converter(
    ulm_sensors_config_helper: Mock,
    request_helper: RequestHelper,
) -> UlmSensorsPullConverter:
    return UlmSensorsPullConverter(config_helper=ulm_sensors_config_helper, request_helper=request_helper)


class UlmSensorsPullConverterTest:
    @staticmethod
    def test_get_static_parking_sites(ulm_sensors_pull_converter: UlmSensorsPullConverter):
        static_parking_site_inputs, import_parking_site_exceptions = (
            ulm_sensors_pull_converter.get_static_parking_sites()
        )

        assert len(static_parking_site_inputs) > len(import_parking_site_exceptions), (
            'There should be more valid than invalid parking sites'
        )

        validate_static_parking_site_inputs(static_parking_site_inputs)

    @staticmethod
    def test_get_realtime_parking_sites(
        ulm_sensors_pull_converter: UlmSensorsPullConverter,
        requests_mock: Mocker,
    ):
        json_path = Path(Path(__file__).parent, 'data', 'ulm-sensors', 'realtime-parking-sites.json')
        with json_path.open() as json_file:
            json_data = json_file.read()

        requests_mock.post(
            'https://citysens-iot.swu.de/auth/realms/ocon/protocol/openid-connect/token',
            json={'access_token': 'token'},
        )
        requests_mock.get(
            'https://citysens-iot.swu.de/consumer-api/v1/collections/sensors/pbg_all_carparks/data', text=json_data
        )

        realtime_parking_site_inputs, import_parking_site_exceptions = (
            ulm_sensors_pull_converter.get_realtime_parking_sites()
        )

        assert len(realtime_parking_site_inputs) == 7
        assert len(import_parking_site_exceptions) == 0

        validate_realtime_parking_site_inputs(realtime_parking_site_inputs)

    @staticmethod
    def test_get_static_parking_spots(ulm_sensors_pull_converter: UlmSensorsPullConverter):
        static_parking_spot_inputs, import_parking_spot_exceptions = (
            ulm_sensors_pull_converter.get_static_parking_spots()
        )

        assert len(static_parking_spot_inputs) > len(import_parking_spot_exceptions), (
            'There should be more valid than invalid parking spots'
        )

        validate_static_parking_spot_inputs(static_parking_spot_inputs)

    @staticmethod
    def test_get_realtime_parking_spots(
        ulm_sensors_pull_converter: UlmSensorsPullConverter,
        requests_mock: Mocker,
    ):
        json_path = Path(Path(__file__).parent, 'data', 'ulm-sensors', 'realtime-parking-spots.json')
        with json_path.open() as json_file:
            json_data = json_file.read()

        sensor_ids = ulm_sensors_pull_converter.config_helper.get('PARK_API_ULM_SENSORS_IDS').split(',')
        for sensor_id in sensor_ids:
            requests_mock.post(
                'https://citysens-iot.swu.de/auth/realms/ocon/protocol/openid-connect/token',
                json={'access_token': 'token'},
            )
            requests_mock.get(
                f'https://citysens-iot.swu.de/consumer-api/v1/collections/sensors/{sensor_id}/data?count=1',
                text=json_data,
            )

        realtime_parking_spot_inputs, import_parking_spot_exceptions = (
            ulm_sensors_pull_converter.get_realtime_parking_spots()
        )

        assert len(realtime_parking_spot_inputs) == 220
        assert len(import_parking_spot_exceptions) == 0

        validate_realtime_parking_spot_inputs(realtime_parking_spot_inputs)
