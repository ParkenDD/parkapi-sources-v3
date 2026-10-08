"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import Mock

import pytest
from requests_mock import Mocker

from parkapi_sources.converters import RadvisBwPullConverter
from parkapi_sources.models.enums import (
    ParkAndRideType,
    ParkingAudience,
    ParkingSiteType,
    PurposeType,
    SupervisionType,
)
from parkapi_sources.util import RequestHelper
from tests.converters.helper import validate_static_parking_site_inputs

SOURCE_URL = (
    'https://radvis.landbw.de/api/geoserver/basicauth/radvis/wfs?service=WFS&version=2.0.0&request=GetFeature'
    '&typeNames=radvis%3Aabstellanlage&outputFormat=application/json'
)


def _config_helper(mocked_config_helper: Mock, ignore_sources: str) -> Mock:
    config = {
        'PARK_API_RADVIS_USER': 'de14131a-c542-445a-999b-88393df54903',
        'PARK_API_RADVIS_PASSWORD': '20832cbc-377d-41e4-aee8-7bc1a87dfe90',
        'PARK_API_RADVIS_IGNORE_SOURCES': ignore_sources,
    }
    mocked_config_helper.get.side_effect = lambda key, default=None: config.get(key, default)
    return mocked_config_helper


@pytest.fixture
def radvis_bw_config_helper(mocked_config_helper: Mock):
    return _config_helper(mocked_config_helper, 'MOBIDATABW')


@pytest.fixture
def radvis_bw_pull_converter(radvis_bw_config_helper: Mock, request_helper: RequestHelper) -> RadvisBwPullConverter:
    return RadvisBwPullConverter(config_helper=radvis_bw_config_helper, request_helper=request_helper)


@pytest.fixture
def radvis_bw_unfiltered_pull_converter(mocked_config_helper: Mock, request_helper: RequestHelper):
    config_helper = _config_helper(mocked_config_helper, 'NO_SUCH_SOURCE')
    return RadvisBwPullConverter(config_helper=config_helper, request_helper=request_helper)


def _mock_source(requests_mock: Mocker):
    json_path = Path(Path(__file__).parent, 'data', 'radvis_bw.json')
    with json_path.open() as json_file:
        json_data = json_file.read()

    requests_mock.get(SOURCE_URL, text=json_data)


class RadvisBwConverterTest:
    @staticmethod
    def test_get_static_parking_sites(radvis_bw_pull_converter: RadvisBwPullConverter, requests_mock: Mocker):
        _mock_source(requests_mock)

        static_parking_site_inputs, import_parking_site_exceptions = radvis_bw_pull_converter.get_static_parking_sites()

        # All parking sites from MOBIDATABW as well as all planned and out of order ones are ignored.
        assert len(static_parking_site_inputs) == 974
        assert len(import_parking_site_exceptions) == 0

        validate_static_parking_site_inputs(static_parking_site_inputs)

    @staticmethod
    def test_get_static_parking_sites_mapping(
        radvis_bw_pull_converter: RadvisBwPullConverter,
        requests_mock: Mocker,
    ):
        _mock_source(requests_mock)

        static_parking_site_inputs, _ = radvis_bw_pull_converter.get_static_parking_sites()
        parking_site_input = next(item for item in static_parking_site_inputs if item.uid == '152443481')

        assert parking_site_input.name == 'Abstellanlage'
        assert parking_site_input.operator_name == 'Ellwangen'
        assert parking_site_input.purpose == PurposeType.BIKE
        assert parking_site_input.type == ParkingSiteType.LOCKERS
        assert parking_site_input.capacity == 24
        assert parking_site_input.has_fee is True
        assert parking_site_input.is_covered is False
        assert parking_site_input.supervision_type == SupervisionType.NO
        assert parking_site_input.related_location == 'Bike and Ride'
        assert parking_site_input.park_and_ride_type == [ParkAndRideType.YES]
        assert parking_site_input.static_data_updated_at == datetime(2026, 8, 26, 18, 50, 27, tzinfo=timezone.utc)
        assert len(parking_site_input.restrictions) == 1
        assert parking_site_input.restrictions[0].type == ParkingAudience.CHARGING
        assert parking_site_input.restrictions[0].capacity == 4

    @staticmethod
    def test_get_static_parking_sites_without_ignored_sources(
        radvis_bw_unfiltered_pull_converter: RadvisBwPullConverter,
        requests_mock: Mocker,
    ):
        _mock_source(requests_mock)

        static_parking_site_inputs, import_parking_site_exceptions = (
            radvis_bw_unfiltered_pull_converter.get_static_parking_sites()
        )

        # Just the planned and out of order parking sites are ignored.
        assert len(static_parking_site_inputs) == 4399
        assert len(import_parking_site_exceptions) == 0

        # Lockboxes are the only parking sites which are no bike parking sites.
        lockbox_inputs = [item for item in static_parking_site_inputs if item.type == ParkingSiteType.LOCKBOX]
        assert len(lockbox_inputs) == 14
        assert all(item.purpose == PurposeType.ITEM for item in lockbox_inputs)
        assert all(
            item.purpose == PurposeType.BIKE
            for item in static_parking_site_inputs
            if item.type != ParkingSiteType.LOCKBOX
        )

        assert len([item for item in static_parking_site_inputs if item.type == ParkingSiteType.SAFE_WALL_LOOPS]) == 26
        assert len([item for item in static_parking_site_inputs if item.type == ParkingSiteType.FLOOR]) == 19

        # A fee of 0 means that the parking site is free of charge.
        assert len([item for item in static_parking_site_inputs if item.has_fee is True]) == 17
        assert len([item for item in static_parking_site_inputs if item.has_fee is False]) == 54

        validate_static_parking_site_inputs(static_parking_site_inputs)
