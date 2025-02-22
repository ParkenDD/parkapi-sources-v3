"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from pathlib import Path
from unittest.mock import Mock

import pytest
from requests_mock import Mocker

from parkapi_sources.converters import RadvisBwPullConverter
from parkapi_sources.util import RequestHelper
from tests.converters.helper import validate_static_parking_site_inputs


@pytest.fixture
def radvis_bw_config_helper(mocked_config_helper: Mock):
    config = {
        'PARK_API_RADVIS_USER': 'de14131a-c542-445a-999b-88393df54903',
        'PARK_API_RADVIS_PASSWORD': '20832cbc-377d-41e4-aee8-7bc1a87dfe90',
        'PARK_API_RADVIS_IGNORE_SOURCES': 'MOBIDATABW',
    }
    mocked_config_helper.get.side_effect = lambda key, default=None: config.get(key, default)
    return mocked_config_helper


@pytest.fixture
def radvis_bw_pull_converter(radvis_bw_config_helper: Mock, request_helper: RequestHelper) -> RadvisBwPullConverter:
    return RadvisBwPullConverter(config_helper=radvis_bw_config_helper, request_helper=request_helper)


class RadvisBwConverterTest:
    @staticmethod
    def test_get_static_parking_sites(radvis_bw_pull_converter: RadvisBwPullConverter, requests_mock: Mocker):
        json_path = Path(Path(__file__).parent, 'data', 'radvis_bw.json')
        with json_path.open() as json_file:
            json_data = json_file.read()

        requests_mock.get(
            'https://radvis.landbw.de/api/geoserver/basicauth/radvis/wfs?service=WFS&version=2.0.0&request=GetFeature'
            '&typeNames=radvis%3Aabstellanlage&outputFormat=application/json',
            text=json_data,
        )
        static_parking_site_inputs, import_parking_site_exceptions = radvis_bw_pull_converter.get_static_parking_sites()

        assert len(static_parking_site_inputs) == 690
        assert len(import_parking_site_exceptions) == 1

        validate_static_parking_site_inputs(static_parking_site_inputs)
