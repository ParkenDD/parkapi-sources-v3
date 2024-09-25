"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from pathlib import Path
from unittest.mock import Mock

import pytest
from parkapi_sources.converters import VrnParkAndRidePullConverter
from requests_mock import Mocker

from tests.converters.helper import validate_realtime_parking_site_inputs, validate_static_parking_site_inputs


@pytest.fixture
def vrn_p_r_config_helper(mocked_config_helper: Mock):
    config = {
        'PARK_API_VRN_P_R_MULTIGUIDE_API_USERNAME': '0152d634-9e16-46c0-bfef-20c0b623eaa3',
        'PARK_API_VRN_P_R_MULTIGUIDE_API_PASSWORD': 'eaf7a00c-d0e1-4464-a9dc-f8ef4d01f2cc',
        'PARK_API_VRN_P_R_SONAH_API_BEARER_TOKEN': '0152d634-9e16-46c0-bfef-20c0b623eaa3',
    }
    mocked_config_helper.get.side_effect = lambda key, default=None: config.get(key, default)
    return mocked_config_helper


@pytest.fixture
def vrn_p_r_pull_converter(vrn_p_r_config_helper: Mock) -> VrnParkAndRidePullConverter:
    return VrnParkAndRidePullConverter(config_helper=vrn_p_r_config_helper)


class VrnParkAndRideBaseConverterTest:
    @staticmethod
    def test_get_static_parking_sites(vrn_p_r_pull_converter: VrnParkAndRidePullConverter, requests_mock: Mocker):
        json_path = Path(Path(__file__).parent, 'data', 'vrn_p_r.json')
        with json_path.open() as json_file:
            json_data = json_file.read()

        requests_mock.get(
            'https://spatial.vrn.de/data/rest/services/Hosted/p_r_parkapi_static/FeatureServer/5/query?where=objectid%3E0&outFields=*&returnGeometry=true&f=geojson',
            text=json_data,
        )

        multiguide_json_path = Path(Path(__file__).parent, 'data', 'vrn_p_r_multiguide.json')
        with multiguide_json_path.open() as json_file:
            multiguide_json_data = json_file.read()

        requests_mock.get(
            'https://vrn.multiguide.info/api/area',
            text=multiguide_json_data,
        )

        sonah_json_path = Path(Path(__file__).parent, 'data', 'vrn_p_r_sonah.json')
        with sonah_json_path.open() as json_file:
            sonah_json_data = json_file.read()

        requests_mock.get(
            'https://vrnm.dyndns.sonah.xyz/api/v3/rest/json/locations',
            text=sonah_json_data,
        )

        static_parking_site_inputs, import_parking_site_exceptions = vrn_p_r_pull_converter.get_static_parking_sites()

        assert len(static_parking_site_inputs) == 12
        assert len(import_parking_site_exceptions) == 0

        validate_static_parking_site_inputs(static_parking_site_inputs)

    @staticmethod
    def test_get_realtime_parking_sites(vrn_p_r_pull_converter: VrnParkAndRidePullConverter, requests_mock: Mocker):
        json_path = Path(Path(__file__).parent, 'data', 'vrn_p_r.json')
        with json_path.open() as json_file:
            json_data = json_file.read()

        requests_mock.get(
            'https://spatial.vrn.de/data/rest/services/Hosted/p_r_parkapi_static/FeatureServer/5/query?where=objectid%3E0&outFields=*&returnGeometry=true&f=geojson',
            text=json_data,
        )

        multiguide_json_path = Path(Path(__file__).parent, 'data', 'vrn_p_r_multiguide.json')
        with multiguide_json_path.open() as json_file:
            multiguide_json_data = json_file.read()

        requests_mock.get(
            'https://vrn.multiguide.info/api/area',
            text=multiguide_json_data,
        )

        sonah_json_path = Path(Path(__file__).parent, 'data', 'vrn_p_r_sonah.json')
        with sonah_json_path.open() as json_file:
            sonah_json_data = json_file.read()

        requests_mock.get(
            'https://vrnm.dyndns.sonah.xyz/api/v3/rest/json/locations',
            text=sonah_json_data,
        )

        realtime_parking_site_inputs, import_parking_site_exceptions = vrn_p_r_pull_converter.get_realtime_parking_sites()

        assert len(realtime_parking_site_inputs) == 12
        assert len(import_parking_site_exceptions) == 0

        validate_realtime_parking_site_inputs(realtime_parking_site_inputs)
