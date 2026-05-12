"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from pathlib import Path
from unittest.mock import Mock

import pytest
from requests_mock import Mocker

from parkapi_sources.converters import KonstanzBikePullConverter
from parkapi_sources.util import RequestHelper
from tests.converters.helper import validate_static_parking_site_inputs


@pytest.fixture
def konstanz_bike_pull_converter(
    mocked_config_helper: Mock, request_helper: RequestHelper
) -> KonstanzBikePullConverter:
    return KonstanzBikePullConverter(config_helper=mocked_config_helper, request_helper=request_helper)


class KonstanzBikePushConverterTest:
    @staticmethod
    def test_get_static_parking_sites(konstanz_bike_pull_converter: KonstanzBikePullConverter, requests_mock: Mocker):
        json_path = Path(Path(__file__).parent, 'data', 'konstanz_bike.geojson')
        with json_path.open() as json_file:
            json_data = json_file.read()

        requests_mock.get(
            'https://services-eu1.arcgis.com/cgMeYTGtzFtnxdsx/arcgis/rest/services/Fahrradverkehr/FeatureServer/7/query?outFields=*&where=1%3D1&f=geojson',
            text=json_data,
        )

        static_parking_site_inputs, import_parking_site_exceptions = (
            konstanz_bike_pull_converter.get_static_parking_sites()
        )

        assert len(static_parking_site_inputs) == 347
        assert len(import_parking_site_exceptions) == 6

        validate_static_parking_site_inputs(static_parking_site_inputs)
