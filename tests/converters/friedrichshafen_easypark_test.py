"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from io import StringIO
from unittest.mock import Mock

import pytest

from parkapi_sources.converters.friedrichshafen_easypark.converter import FriedrichshafenEasyParkPushConverter
from parkapi_sources.models.enums import ParkingAudience
from parkapi_sources.util import RequestHelper
from tests.converters.helper import get_data_path, validate_static_parking_site_inputs


@pytest.fixture
def friedrichshafen_easypark_push_converter(
    mocked_config_helper: Mock, request_helper: RequestHelper
) -> FriedrichshafenEasyParkPushConverter:
    return FriedrichshafenEasyParkPushConverter(config_helper=mocked_config_helper, request_helper=request_helper)


class FriedrichshafenEasyParkPushConverterTest:
    @staticmethod
    def test_get_static_parking_sites(friedrichshafen_easypark_push_converter: FriedrichshafenEasyParkPushConverter):
        with get_data_path('friedrichshafen_easypark.csv').open() as friedrichshafen_easypark_file:
            friedrichshafen_easypark_data = StringIO(friedrichshafen_easypark_file.read())

        static_parking_site_inputs, import_parking_site_exceptions = (
            friedrichshafen_easypark_push_converter.handle_csv_string(friedrichshafen_easypark_data)
        )

        assert len(static_parking_site_inputs) == 1681
        assert len(import_parking_site_exceptions) == 0

        static_parking_site_inputs_by_uid = {item.uid: item for item in static_parking_site_inputs}

        free_parking_site = static_parking_site_inputs_by_uid['1']
        assert free_parking_site.has_fee is False
        assert free_parking_site.restrictions == []
        # The trailing whitespace of the source value has to be stripped
        assert free_parking_site.description == 'Gebührenfreies Parken'
        assert free_parking_site.fee_description == 'Gebührenfreies Parken'

        resident_parking_site = static_parking_site_inputs_by_uid['22']
        assert resident_parking_site.has_fee is True
        assert [restriction.type for restriction in resident_parking_site.restrictions] == [ParkingAudience.RESIDENT]
        assert resident_parking_site.fee_description == (
            'Gebührenpflichtiges Parken/Bewohnerparken; '
            'Gebührenfrei: Mo-Sa 0-8 20-24 So 0-24; '
            'Gebührenpflichtiges Parken/Bewohnerparken: Mo-Sa 8-20'
        )

        disabled_parking_site = static_parking_site_inputs_by_uid['18']
        assert disabled_parking_site.has_fee is False
        assert [restriction.type for restriction in disabled_parking_site.restrictions] == [ParkingAudience.DISABLED]

        validate_static_parking_site_inputs(static_parking_site_inputs)
