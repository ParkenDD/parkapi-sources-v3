"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from parkapi_sources.converters import BietigheimBissingenPullConverter
from parkapi_sources.util import RequestHelper
from tests.converters.helper import validate_realtime_parking_site_inputs, validate_static_parking_site_inputs


@pytest.fixture
def bietigheim_bissingen_config_helper(mocked_config_helper: Mock):
    config = {
        'STATIC_GEOJSON_BASE_URL': 'https://raw.githubusercontent.com/ParkenDD/parkapi-static-data/main/sources',
        'PARK_API_BIETIGHEIM_BISSINGEN_USER': '0152d634-9e16-46c0-bfef-20c0b623eaa3',
        'PARK_API_BIETIGHEIM_BISSINGEN_PASSWORD': 'eaf7a00c-d0e1-4464-a9dc-f8ef4d01f2cc',
    }
    mocked_config_helper.get.side_effect = lambda key, default=None: config.get(key, default)
    return mocked_config_helper


@pytest.fixture
def bietigheim_bissingen_pull_converter(
    bietigheim_bissingen_config_helper: Mock,
    request_helper: RequestHelper,
) -> BietigheimBissingenPullConverter:
    return BietigheimBissingenPullConverter(
        config_helper=bietigheim_bissingen_config_helper,
        request_helper=request_helper,
    )


class BietigheimBissingenPullConverterTest:
    @staticmethod
    def test_get_static_parking_sites(bietigheim_bissingen_pull_converter: BietigheimBissingenPullConverter):
        static_parking_site_inputs, import_parking_site_exceptions = (
            bietigheim_bissingen_pull_converter.get_static_parking_sites()
        )

        assert len(static_parking_site_inputs) > len(import_parking_site_exceptions), (
            'There should be more valid then invalid parking sites'
        )

        validate_static_parking_site_inputs(static_parking_site_inputs)

    @staticmethod
    def test_get_realtime_parking_sites(bietigheim_bissingen_pull_converter: BietigheimBissingenPullConverter):
        # we need to patch _get_data as there is no realistic way to mock the whole IMAP process
        csv_path = Path(Path(__file__).parent, 'data', 'bietigheim-bissingen.csv')
        with csv_path.open('rb') as csv_file:
            csv_data = csv_file.read()

        with patch.object(BietigheimBissingenPullConverter, '_get_data', return_value=csv_data) as mock_method:
            realtime_parking_site_inputs, import_parking_site_exceptions = (
                bietigheim_bissingen_pull_converter.get_realtime_parking_sites()
            )

        mock_method.assert_called()

        assert len(realtime_parking_site_inputs) == 14
        assert len(import_parking_site_exceptions) == 0

        validate_realtime_parking_site_inputs(realtime_parking_site_inputs)
