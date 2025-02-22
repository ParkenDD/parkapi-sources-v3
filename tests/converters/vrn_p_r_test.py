"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from pathlib import Path
from unittest.mock import Mock

import pytest
from requests_mock import Mocker

from parkapi_sources.converters import VrnParkAndRidePullConverter
from parkapi_sources.util import RequestHelper
from tests.converters.helper import validate_realtime_parking_site_inputs, validate_static_parking_site_inputs


@pytest.fixture
def vrn_p_r_pull_converter(
    mocked_static_geojson_config_helper: Mock,
    request_helper: RequestHelper,
) -> VrnParkAndRidePullConverter:
    return VrnParkAndRidePullConverter(
        config_helper=mocked_static_geojson_config_helper,
        request_helper=request_helper,
    )


class VrnParkAndRidePullConverterTest:
    @staticmethod
    def test_get_static_parking_sites(vrn_p_r_pull_converter: VrnParkAndRidePullConverter, requests_mock: Mocker):
        # We need to get GeoJSON data
        requests_mock.real_http = True

        json_path = Path(Path(__file__).parent, 'data', 'vrn_p_r.json')
        with json_path.open() as json_file:
            json_data = json_file.read()

        requests_mock.get(
            'https://spatial.vrn.de/data/rest/services/P_R_Sensorik__Realtime_/FeatureServer/0/query?where=1%3D1&outFields=*&f=geojson',
            text=json_data,
        )

        static_parking_site_inputs, import_parking_site_exceptions = vrn_p_r_pull_converter.get_static_parking_sites()

        assert len(static_parking_site_inputs) == 12
        assert len(import_parking_site_exceptions) == 2

        validate_static_parking_site_inputs(static_parking_site_inputs)

    @staticmethod
    def test_get_realtime_parking_sites(vrn_p_r_pull_converter: VrnParkAndRidePullConverter, requests_mock: Mocker):
        json_path = Path(Path(__file__).parent, 'data', 'vrn_p_r.json')
        with json_path.open() as json_file:
            json_data = json_file.read()

        requests_mock.get(
            'https://spatial.vrn.de/data/rest/services/P_R_Sensorik__Realtime_/FeatureServer/0/query?where=1%3D1&outFields=*&f=geojson',
            text=json_data,
        )

        realtime_parking_site_inputs, import_parking_site_exceptions = (
            vrn_p_r_pull_converter.get_realtime_parking_sites()
        )

        assert len(realtime_parking_site_inputs) == 12
        assert len(import_parking_site_exceptions) == 2

        validate_realtime_parking_site_inputs(realtime_parking_site_inputs)
