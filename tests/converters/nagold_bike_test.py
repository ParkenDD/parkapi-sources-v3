"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import json
from datetime import datetime, timezone
from unittest.mock import Mock

import pytest

from parkapi_sources.converters import NagoldBikePushConverter
from parkapi_sources.models.enums import (
    ParkAndRideType,
    ParkingAudience,
    ParkingSiteType,
    PurposeType,
    SupervisionType,
)
from parkapi_sources.util import RequestHelper
from tests.converters.helper import get_data_path, validate_static_parking_site_inputs


@pytest.fixture
def nagold_bike_push_converter(
    mocked_config_helper: Mock,
    request_helper: RequestHelper,
) -> NagoldBikePushConverter:
    return NagoldBikePushConverter(config_helper=mocked_config_helper, request_helper=request_helper)


@pytest.fixture
def nagold_bike_data() -> dict:
    with get_data_path('nagold_bike.geojson').open() as nagold_bike_file:
        return json.loads(nagold_bike_file.read())


class NagoldBikePushConverterTest:
    @staticmethod
    def test_get_static_parking_sites(nagold_bike_push_converter: NagoldBikePushConverter, nagold_bike_data: dict):
        static_parking_site_inputs, import_parking_site_exceptions = nagold_bike_push_converter.handle_json(
            nagold_bike_data,
        )

        # The source has 37 features, one of them is a placeholder without stand type and capacity. One feature has
        # lockers and therefore results in two ParkingSites.
        assert len(static_parking_site_inputs) == 37
        assert len(import_parking_site_exceptions) == 0

        validate_static_parking_site_inputs(static_parking_site_inputs)

    @staticmethod
    def test_static_parking_site_mapping(
        nagold_bike_push_converter: NagoldBikePushConverter,
        nagold_bike_data: dict,
    ):
        static_parking_site_inputs, _ = nagold_bike_push_converter.handle_json(nagold_bike_data)
        parking_sites_by_uid = {item.uid: item for item in static_parking_site_inputs}

        parking_site = parking_sites_by_uid['809']
        assert parking_site.name == 'Oberamteistraße'
        assert parking_site.address == 'Oberamteistraße, 72202 Nagold'
        assert parking_site.description == 'Am Parkplatz vom Polizeirevier'
        assert parking_site.purpose == PurposeType.BIKE
        assert parking_site.type == ParkingSiteType.WALL_LOOPS
        assert parking_site.capacity == 4
        assert float(parking_site.lat) == pytest.approx(48.5520391)
        assert float(parking_site.lon) == pytest.approx(8.7219905)
        assert parking_site.has_lighting is True
        assert parking_site.is_covered is False
        assert parking_site.opening_hours == '24/7'
        assert parking_site.park_and_ride_type == [ParkAndRideType.NO]
        assert parking_site.supervision_type == SupervisionType.NO
        assert parking_site.operator_name is None
        assert parking_site.restrictions == []
        assert parking_site.has_realtime_data is False
        assert parking_site.static_data_updated_at == datetime(2024, 9, 27, 0, 0, tzinfo=timezone.utc)

        # Anlehnbügel maps to STANDS, Bike_and_R "ja" maps to park and ride YES
        assert parking_sites_by_uid['422'].type == ParkingSiteType.STANDS
        assert parking_sites_by_uid['422'].park_and_ride_type == [ParkAndRideType.YES]

    @staticmethod
    def test_charging_restriction(nagold_bike_push_converter: NagoldBikePushConverter, nagold_bike_data: dict):
        static_parking_site_inputs, _ = nagold_bike_push_converter.handle_json(nagold_bike_data)

        parking_sites_with_charging = [item for item in static_parking_site_inputs if item.restrictions]

        assert len(parking_sites_with_charging) == 1
        assert len(parking_sites_with_charging[0].restrictions) == 1
        assert parking_sites_with_charging[0].restrictions[0].type == ParkingAudience.CHARGING
        assert parking_sites_with_charging[0].restrictions[0].capacity == 4

    @staticmethod
    def test_lockers_parking_site(nagold_bike_push_converter: NagoldBikePushConverter, nagold_bike_data: dict):
        static_parking_site_inputs, _ = nagold_bike_push_converter.handle_json(nagold_bike_data)
        parking_sites_by_uid = {item.uid: item for item in static_parking_site_inputs}

        lockers_parking_sites = [item for item in static_parking_site_inputs if item.type == ParkingSiteType.LOCKERS]
        assert len(lockers_parking_sites) == 1

        stands_parking_site = parking_sites_by_uid['412']
        lockers_parking_site = parking_sites_by_uid['412-lockers']

        assert lockers_parking_site is lockers_parking_sites[0]
        assert lockers_parking_site.name == 'Calwer Straße (Schließfächer)'
        assert lockers_parking_site.capacity == 4
        assert lockers_parking_site.purpose == PurposeType.BIKE

        # The lockers share location, description and all attributes of the surrounding installation
        assert lockers_parking_site.lat == stands_parking_site.lat
        assert lockers_parking_site.lon == stands_parking_site.lon
        assert lockers_parking_site.address == stands_parking_site.address
        assert lockers_parking_site.description == stands_parking_site.description
        assert lockers_parking_site.static_data_updated_at == stands_parking_site.static_data_updated_at

        # The stands keep their own type and capacity, the charging restriction stays with them
        assert stands_parking_site.type == ParkingSiteType.STANDS
        assert stands_parking_site.capacity == 8
        assert lockers_parking_site.restrictions == []

    @staticmethod
    def test_fee_is_empty_in_source_data(nagold_bike_push_converter: NagoldBikePushConverter, nagold_bike_data: dict):
        static_parking_site_inputs, _ = nagold_bike_push_converter.handle_json(nagold_bike_data)

        assert all(item.has_fee is None for item in static_parking_site_inputs)
        assert all(item.fee_description is None for item in static_parking_site_inputs)

    @staticmethod
    def test_fee_mapping(nagold_bike_push_converter: NagoldBikePushConverter, nagold_bike_data: dict):
        nagold_bike_data['features'][0]['properties'] |= {
            'Gebueren_p': 'ja',
            'Gebueren_1': '1 € pro Tag',
            'Gebueren_2': '15 € pro Monat',
        }
        nagold_bike_data['features'][1]['properties']['Gebueren_p'] = 'nein'

        static_parking_site_inputs, _ = nagold_bike_push_converter.handle_json(nagold_bike_data)
        parking_sites_by_uid = {item.uid: item for item in static_parking_site_inputs}

        assert parking_sites_by_uid['809'].has_fee is True
        assert parking_sites_by_uid['809'].fee_description == '1 € pro Tag, 15 € pro Monat'

        assert parking_sites_by_uid['413'].has_fee is False
        assert parking_sites_by_uid['413'].fee_description is None

    @staticmethod
    def test_invalid_feature_is_reported(nagold_bike_push_converter: NagoldBikePushConverter, nagold_bike_data: dict):
        nagold_bike_data['features'][0]['properties']['Stellplatz'] = 'Fahrradgarage'

        static_parking_site_inputs, import_parking_site_exceptions = nagold_bike_push_converter.handle_json(
            nagold_bike_data,
        )

        assert len(static_parking_site_inputs) == 36
        assert len(import_parking_site_exceptions) == 1
        assert import_parking_site_exceptions[0].parking_site_uid == '809'
