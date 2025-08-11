"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from pathlib import Path
from unittest.mock import Mock

import pytest
from requests_mock import Mocker

from parkapi_sources.converters import FreiburgDisabledSensorsPullConverter
from parkapi_sources.util import RequestHelper
from tests.converters.helper import validate_realtime_parking_spot_inputs, validate_static_parking_spot_inputs


@pytest.fixture
def freiburg_disabled_sensors_pull_converter(
    mocked_config_helper: Mock,
    request_helper: RequestHelper,
) -> FreiburgDisabledSensorsPullConverter:
    return FreiburgDisabledSensorsPullConverter(
        config_helper=mocked_config_helper,
        request_helper=request_helper,
    )


@pytest.fixture
def requests_mock_freiburg_disabled_sensors(requests_mock: Mocker) -> Mocker:
    json_path = Path(Path(__file__).parent, 'data', 'freiburg_disabled_sensors.geojson')
    with json_path.open() as json_file:
        json_data = json_file.read()

    requests_mock.get(
        'https://geoportal.freiburg.de/wfs/gdm_parkpl/gdm_parkpl?SERVICE=WFS&REQUEST=GetFeature&SRSNAME=EPSG:4326'
        '&SERVICE=WFS&VERSION=2.0.0&TYPENAMES=beh_parkpl_ueberw&OUTPUTFORMAT=geojson',
        text=json_data,
    )

    return requests_mock


class FreiburgDisabledSensorsConverterTest:
    @staticmethod
    def test_get_static_parking_spots(
        freiburg_disabled_sensors_pull_converter: FreiburgDisabledSensorsPullConverter,
        requests_mock_freiburg_disabled_sensors: Mocker,
    ):
        static_parking_spot_inputs, import_parking_spot_exceptions = (
            freiburg_disabled_sensors_pull_converter.get_static_parking_spots()
        )

        assert len(static_parking_spot_inputs) == 20
        assert len(import_parking_spot_exceptions) == 0

        validate_static_parking_spot_inputs(static_parking_spot_inputs)

    @staticmethod
    def test_get_realtime_parking_spots(
        freiburg_disabled_sensors_pull_converter: FreiburgDisabledSensorsPullConverter,
        requests_mock_freiburg_disabled_sensors: Mocker,
    ):
        realtime_parking_spot_inputs, import_parking_spot_exceptions = (
            freiburg_disabled_sensors_pull_converter.get_realtime_parking_spots()
        )

        assert len(realtime_parking_spot_inputs) == 20
        assert len(import_parking_spot_exceptions) == 0

        validate_realtime_parking_spot_inputs(realtime_parking_spot_inputs)
