"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from decimal import Decimal
from pathlib import Path
from unittest.mock import Mock

import pytest
from requests_mock import Mocker
from validataclass.validators import DataclassValidator

from parkapi_sources.converters import KienzlerBikeAndRidePullConverter
from parkapi_sources.converters.kienzler.models import KienzlerGeojsonFeatureInput
from parkapi_sources.models.enums import ExternalIdentifierType, ParkAndRideType
from parkapi_sources.util import RequestHelper
from tests.converters.helper import validate_realtime_parking_site_inputs, validate_static_parking_site_inputs


@pytest.fixture
def requests_mock_kienzler(requests_mock: Mocker) -> Mocker:
    json_path = Path(Path(__file__).parent, 'data', 'kienzler.json')
    with json_path.open() as json_file:
        json_data = json_file.read()

    requests_mock.post('https://www.bikeandridebox.de/index.php', text=json_data)

    return requests_mock


@pytest.fixture
def requests_mock_kienzler_with_geojson(requests_mock: Mocker) -> Mocker:
    json_path = Path(Path(__file__).parent, 'data', 'kienzler.geojson')
    with json_path.open() as json_file:
        json_data = json_file.read()

    requests_mock.get(
        'mock://geojson-url/kienzler_bike_and_ride.geojson',
        text=json_data,
    )

    return requests_mock


@pytest.fixture
def kienzler_config_helper(mocked_config_helper: Mock):
    config = {
        'PARK_API_KIENZLER_BIKE_AND_RIDE_USER': '01275925-742c-460b-8778-eca90eb114bc',
        'PARK_API_KIENZLER_BIKE_AND_RIDE_PASSWORD': '626027f2-66e9-40bd-8ff2-4c010f5eca05',
        'PARK_API_KIENZLER_BIKE_AND_RIDE_IDS': 'id1,id2,id3',
        'STATIC_GEOJSON_BASE_URL': 'mock://geojson-url',
    }
    mocked_config_helper.get.side_effect = lambda key, default=None: config.get(key, default)
    return mocked_config_helper


@pytest.fixture
def kienzler_pull_converter(
    kienzler_config_helper: Mock,
    request_helper: RequestHelper,
) -> KienzlerBikeAndRidePullConverter:
    return KienzlerBikeAndRidePullConverter(config_helper=kienzler_config_helper, request_helper=request_helper)


@pytest.fixture
def kienzler_pull_converter_with_geojson(
    kienzler_config_helper: Mock,
    request_helper: RequestHelper,
) -> KienzlerBikeAndRidePullConverter:
    converter = KienzlerBikeAndRidePullConverter(config_helper=kienzler_config_helper, request_helper=request_helper)
    converter.use_geojson = True
    converter.geojson_feature_validator = DataclassValidator(KienzlerGeojsonFeatureInput)
    return converter


class KienzlerPullConverterTest:
    @staticmethod
    def test_get_static_parking_sites(
        kienzler_pull_converter: KienzlerBikeAndRidePullConverter,
        requests_mock_kienzler: Mocker,
    ):
        static_parking_site_inputs, import_parking_site_exceptions = kienzler_pull_converter.get_static_parking_sites()

        assert len(static_parking_site_inputs) == 5
        assert len(import_parking_site_exceptions) == 0

        validate_static_parking_site_inputs(static_parking_site_inputs)

    @staticmethod
    def test_get_static_parking_sites_with_geojson(
        kienzler_pull_converter_with_geojson: KienzlerBikeAndRidePullConverter,
        requests_mock_kienzler: Mocker,
        requests_mock_kienzler_with_geojson: Mocker,
    ):
        static_parking_site_inputs, import_parking_site_exceptions = (
            kienzler_pull_converter_with_geojson.get_static_parking_sites()
        )

        assert len(static_parking_site_inputs) == 5
        assert len(import_parking_site_exceptions) == 0

        # Check that the data has been updated
        static_parking_site_input = next(iter(item for item in static_parking_site_inputs if item.uid == 'unit1676'))

        assert static_parking_site_input.uid == 'unit1676'
        assert static_parking_site_input.type.value == 'TWO_TIER'
        assert static_parking_site_input.max_height == 1250
        assert static_parking_site_input.max_width == 800
        assert static_parking_site_input.park_and_ride_type == [ParkAndRideType.TRAIN]
        assert static_parking_site_input.external_identifiers[0].type == ExternalIdentifierType.DHID
        assert static_parking_site_input.external_identifiers[0].value == 'de:08317:14500_Parent'
        assert static_parking_site_input.lat == Decimal('48.475546')
        assert static_parking_site_input.lon == Decimal('7.947474')

        validate_static_parking_site_inputs(static_parking_site_inputs)

    @staticmethod
    def test_get_realtime_parking_sites(
        kienzler_pull_converter: KienzlerBikeAndRidePullConverter,
        requests_mock_kienzler: Mocker,
    ):
        realtime_parking_site_inputs, import_parking_site_exceptions = (
            kienzler_pull_converter.get_realtime_parking_sites()
        )

        assert len(realtime_parking_site_inputs) == 5
        assert len(import_parking_site_exceptions) == 0

        validate_realtime_parking_site_inputs(realtime_parking_site_inputs)
