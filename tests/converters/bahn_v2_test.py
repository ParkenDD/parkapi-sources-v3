"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from pathlib import Path
from unittest.mock import Mock

import pytest
from requests_mock import Mocker

from parkapi_sources.converters.bahn_v2 import BahnV2PullConverter
from parkapi_sources.util import RequestHelper
from tests.converters.helper import validate_static_parking_site_inputs


@pytest.fixture
def bahn_v2_config_helper(mocked_config_helper: Mock):
    config = {
        'PARK_API_BAHN_API_CLIENT_ID': 'de14131a-c542-445a-999b-88393df54903',
        'PARK_API_BAHN_API_CLIENT_SECRET': '20832cbc-377d-41e4-aee8-7bc1a87dfe90',
    }
    mocked_config_helper.get.side_effect = lambda key, default=None: config.get(key, default)
    return mocked_config_helper


@pytest.fixture
def bahn_v2_pull_converter(bahn_v2_config_helper: Mock, request_helper: RequestHelper) -> BahnV2PullConverter:
    return BahnV2PullConverter(config_helper=bahn_v2_config_helper, request_helper=request_helper)


class BahnV2PullConverterTest:
    @staticmethod
    def test_get_static_parking_sites(bahn_v2_pull_converter: BahnV2PullConverter, requests_mock: Mocker):
        json_path = Path(Path(__file__).parent, 'data', 'bahn_v2.json')
        with json_path.open() as json_file:
            json_data = json_file.read()

        requests_mock.get(
            'https://apis.deutschebahn.com/db-api-marketplace/apis/parking-information/db-bahnpark/v2/parking-facilities',
            text=json_data,
        )

        static_parking_site_inputs, import_parking_site_exceptions = bahn_v2_pull_converter.get_static_parking_sites()

        assert len(static_parking_site_inputs) == 342
        assert len(import_parking_site_exceptions) == 1

        validate_static_parking_site_inputs(static_parking_site_inputs)
