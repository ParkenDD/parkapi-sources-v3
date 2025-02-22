"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime
from pathlib import Path
from unittest.mock import Mock

import pytest
from requests_mock import Mocker

from parkapi_sources.converters.apcoa import ApcoaPullConverter
from parkapi_sources.converters.apcoa.validators import (
    ApcoaAdressInput,
    ApcoaCarparkTypeNameInput,
    ApcoaOpeningHoursInput,
    ApcoaOpeningHoursWeekday,
    ApcoaParkingSiteInput,
    ApcoaParkingSpaceInput,
    ApcoaParkingSpaceType,
)
from parkapi_sources.util import RequestHelper
from tests.converters.helper import validate_static_parking_site_inputs


@pytest.fixture
def apcoa_config_helper(mocked_config_helper: Mock):
    config = {
        'PARK_API_APCOA_API_SUBSCRIPTION_KEY': '9be98961de004749aac8a1d8160e9eba',
    }
    mocked_config_helper.get.side_effect = lambda key, default=None: config.get(key, default)
    return mocked_config_helper


@pytest.fixture
def apcoa_ignore_missing_coordinates_config_helper(mocked_config_helper: Mock):
    config = {
        'PARK_API_APCOA_API_SUBSCRIPTION_KEY': '9be98961de004749aac8a1d8160e9eba',
        'PARK_API_APCOA_IGNORE_MISSING_COORDINATES': True,
    }
    mocked_config_helper.get.side_effect = lambda key, default=None: config.get(key, default)
    return mocked_config_helper


@pytest.fixture
def apcoa_pull_converter(apcoa_config_helper: Mock, request_helper: RequestHelper) -> ApcoaPullConverter:
    return ApcoaPullConverter(config_helper=apcoa_config_helper, request_helper=request_helper)


@pytest.fixture
def apcoa_ignore_missing_coordinates_pull_converter(
    apcoa_ignore_missing_coordinates_config_helper: Mock, request_helper: RequestHelper
) -> ApcoaPullConverter:
    return ApcoaPullConverter(
        config_helper=apcoa_ignore_missing_coordinates_config_helper,
        request_helper=request_helper,
    )


class ApcoaPullConverterTest:
    @staticmethod
    def test_get_static_parking_sites(apcoa_pull_converter: ApcoaPullConverter, requests_mock: Mocker):
        json_path = Path(Path(__file__).parent, 'data', 'apcoa.json')
        with json_path.open() as json_file:
            json_data = json_file.read()

        requests_mock.get(
            'https://api.apcoa-services.com/carpark/v4/Carparks',
            text=json_data,
        )

        static_parking_site_inputs, import_parking_site_exceptions = apcoa_pull_converter.get_static_parking_sites()

        assert len(static_parking_site_inputs) == 329
        assert len(import_parking_site_exceptions) == 24

        validate_static_parking_site_inputs(static_parking_site_inputs)

    @staticmethod
    def test_get_static_parking_sites_ignore_missing_coordinates(
        apcoa_ignore_missing_coordinates_pull_converter: ApcoaPullConverter,
        requests_mock: Mocker,
    ):
        json_path = Path(Path(__file__).parent, 'data', 'apcoa.json')
        with json_path.open() as json_file:
            json_data = json_file.read()

        requests_mock.get(
            'https://api.apcoa-services.com/carpark/v4/Carparks',
            text=json_data,
        )

        static_parking_site_inputs, import_parking_site_exceptions = (
            apcoa_ignore_missing_coordinates_pull_converter.get_static_parking_sites()
        )

        assert len(static_parking_site_inputs) == 329
        assert len(import_parking_site_exceptions) == 19

        validate_static_parking_site_inputs(static_parking_site_inputs)


class ApcoaParkingSiteInputTest:
    @staticmethod
    @pytest.mark.parametrize(
        'opening_times, osm_opening_hours',
        [
            # Test for 24/7
            (
                [
                    ApcoaOpeningHoursInput(
                        Weekday=ApcoaOpeningHoursWeekday.MONDAY,
                        OpeningTimes='00:00 - 00:00',
                    ),
                    ApcoaOpeningHoursInput(
                        Weekday=ApcoaOpeningHoursWeekday.TUESDAY,
                        OpeningTimes='00:00 - 00:00',
                    ),
                    ApcoaOpeningHoursInput(
                        Weekday=ApcoaOpeningHoursWeekday.WEDNESDAY,
                        OpeningTimes='00:00 - 00:00',
                    ),
                    ApcoaOpeningHoursInput(
                        Weekday=ApcoaOpeningHoursWeekday.THURSDAY,
                        OpeningTimes='00:00 - 00:00',
                    ),
                    ApcoaOpeningHoursInput(
                        Weekday=ApcoaOpeningHoursWeekday.FRIDAY,
                        OpeningTimes='00:00 - 00:00',
                    ),
                    ApcoaOpeningHoursInput(
                        Weekday=ApcoaOpeningHoursWeekday.SATURDAY,
                        OpeningTimes='00:00 - 00:00',
                    ),
                    ApcoaOpeningHoursInput(
                        Weekday=ApcoaOpeningHoursWeekday.SUNDAY,
                        OpeningTimes='00:00 - 00:00',
                    ),
                ],
                '24/7',
            ),
            # Test for weekday all the same and separate times at saturday and sunday
            (
                [
                    ApcoaOpeningHoursInput(
                        Weekday=ApcoaOpeningHoursWeekday.MONDAY,
                        OpeningTimes='10:00 - 20:00',
                    ),
                    ApcoaOpeningHoursInput(
                        Weekday=ApcoaOpeningHoursWeekday.TUESDAY,
                        OpeningTimes='10:00 - 20:00',
                    ),
                    ApcoaOpeningHoursInput(
                        Weekday=ApcoaOpeningHoursWeekday.WEDNESDAY,
                        OpeningTimes='10:00 - 20:00',
                    ),
                    ApcoaOpeningHoursInput(
                        Weekday=ApcoaOpeningHoursWeekday.THURSDAY,
                        OpeningTimes='10:00 - 20:00',
                    ),
                    ApcoaOpeningHoursInput(
                        Weekday=ApcoaOpeningHoursWeekday.FRIDAY,
                        OpeningTimes='10:00 - 20:00',
                    ),
                    ApcoaOpeningHoursInput(
                        Weekday=ApcoaOpeningHoursWeekday.SATURDAY,
                        OpeningTimes='10:00 - 16:00',
                    ),
                    ApcoaOpeningHoursInput(
                        Weekday=ApcoaOpeningHoursWeekday.SUNDAY,
                        OpeningTimes='10:00 - 16:00',
                    ),
                ],
                'Mo-Fr 10:00-20:00; Sa 10:00-16:00; Su 10:00-16:00',
                # Even better, but more complicated: 'Mo-Fr 10:00-20:00; Sa-So 10:00-16:00'
            ),
            # Test for different times at Friday
            (
                [
                    ApcoaOpeningHoursInput(
                        Weekday=ApcoaOpeningHoursWeekday.MONDAY,
                        OpeningTimes='10:00 - 20:00',
                    ),
                    ApcoaOpeningHoursInput(
                        Weekday=ApcoaOpeningHoursWeekday.TUESDAY,
                        OpeningTimes='10:00 - 20:00',
                    ),
                    ApcoaOpeningHoursInput(
                        Weekday=ApcoaOpeningHoursWeekday.WEDNESDAY,
                        OpeningTimes='10:00 - 20:00',
                    ),
                    ApcoaOpeningHoursInput(
                        Weekday=ApcoaOpeningHoursWeekday.THURSDAY,
                        OpeningTimes='10:00 - 20:00',
                    ),
                    ApcoaOpeningHoursInput(
                        Weekday=ApcoaOpeningHoursWeekday.FRIDAY,
                        OpeningTimes='10:00 - 16:00',
                    ),
                    ApcoaOpeningHoursInput(
                        Weekday=ApcoaOpeningHoursWeekday.SATURDAY,
                        OpeningTimes='10:00 - 16:00',
                    ),
                    ApcoaOpeningHoursInput(
                        Weekday=ApcoaOpeningHoursWeekday.SUNDAY,
                        OpeningTimes='10:00 - 16:00',
                    ),
                ],
                'Mo 10:00-20:00; Tu 10:00-20:00; We 10:00-20:00; Th 10:00-20:00; Fr 10:00-16:00; Sa 10:00-16:00; Su 10:00-16:00',
                # Even better, but more complicated: 'Mo-Th 10:00-20:00; Fr-So 10:00-16:00'
            ),
            # Test for Sunday missing
            (
                [
                    ApcoaOpeningHoursInput(
                        Weekday=ApcoaOpeningHoursWeekday.MONDAY,
                        OpeningTimes='10:00 - 20:00',
                    ),
                    ApcoaOpeningHoursInput(
                        Weekday=ApcoaOpeningHoursWeekday.TUESDAY,
                        OpeningTimes='10:00 - 20:00',
                    ),
                    ApcoaOpeningHoursInput(
                        Weekday=ApcoaOpeningHoursWeekday.WEDNESDAY,
                        OpeningTimes='10:00 - 20:00',
                    ),
                    ApcoaOpeningHoursInput(
                        Weekday=ApcoaOpeningHoursWeekday.THURSDAY,
                        OpeningTimes='10:00 - 20:00',
                    ),
                    ApcoaOpeningHoursInput(
                        Weekday=ApcoaOpeningHoursWeekday.FRIDAY,
                        OpeningTimes='10:00 - 20:00',
                    ),
                    ApcoaOpeningHoursInput(
                        Weekday=ApcoaOpeningHoursWeekday.SATURDAY,
                        OpeningTimes='10:00 - 16:00',
                    ),
                ],
                'Mo-Fr 10:00-20:00; Sa 10:00-16:00',
            ),
            # Test for Wednesday missing
            (
                [
                    ApcoaOpeningHoursInput(
                        Weekday=ApcoaOpeningHoursWeekday.MONDAY,
                        OpeningTimes='10:00 - 20:00',
                    ),
                    ApcoaOpeningHoursInput(
                        Weekday=ApcoaOpeningHoursWeekday.TUESDAY,
                        OpeningTimes='10:00 - 20:00',
                    ),
                    ApcoaOpeningHoursInput(
                        Weekday=ApcoaOpeningHoursWeekday.THURSDAY,
                        OpeningTimes='10:00 - 20:00',
                    ),
                    ApcoaOpeningHoursInput(
                        Weekday=ApcoaOpeningHoursWeekday.FRIDAY,
                        OpeningTimes='10:00 - 20:00',
                    ),
                    ApcoaOpeningHoursInput(
                        Weekday=ApcoaOpeningHoursWeekday.SATURDAY,
                        OpeningTimes='10:00 - 16:00',
                    ),
                    ApcoaOpeningHoursInput(
                        Weekday=ApcoaOpeningHoursWeekday.SUNDAY,
                        OpeningTimes='10:00 - 16:00',
                    ),
                ],
                'Mo 10:00-20:00; Tu 10:00-20:00; Th 10:00-20:00; Fr 10:00-20:00; Sa 10:00-16:00; Su 10:00-16:00',
                # Even better, but more complicated: 'Mo-Tu 10:00-20:00; Th-Fr 10:00-20:00; Sa-So 10:00-16:00'
            ),
            # Test for all day open at weekday, but not open at weekend
            (
                [
                    ApcoaOpeningHoursInput(
                        Weekday=ApcoaOpeningHoursWeekday.MONDAY,
                        OpeningTimes='00:00 - 00:00',
                    ),
                    ApcoaOpeningHoursInput(
                        Weekday=ApcoaOpeningHoursWeekday.TUESDAY,
                        OpeningTimes='00:00 - 00:00',
                    ),
                    ApcoaOpeningHoursInput(
                        Weekday=ApcoaOpeningHoursWeekday.WEDNESDAY,
                        OpeningTimes='00:00 - 00:00',
                    ),
                    ApcoaOpeningHoursInput(
                        Weekday=ApcoaOpeningHoursWeekday.THURSDAY,
                        OpeningTimes='00:00 - 00:00',
                    ),
                    ApcoaOpeningHoursInput(
                        Weekday=ApcoaOpeningHoursWeekday.FRIDAY,
                        OpeningTimes='00:00 - 00:00',
                    ),
                ],
                'Mo-Fr 00:00-24:00',
            ),
            # Test for different times ending with 00:00 instead of 24:00
            (
                [
                    ApcoaOpeningHoursInput(
                        Weekday=ApcoaOpeningHoursWeekday.MONDAY,
                        OpeningTimes='05:00 - 00:00',
                    ),
                    ApcoaOpeningHoursInput(
                        Weekday=ApcoaOpeningHoursWeekday.TUESDAY,
                        OpeningTimes='05:00 - 00:00',
                    ),
                    ApcoaOpeningHoursInput(
                        Weekday=ApcoaOpeningHoursWeekday.WEDNESDAY,
                        OpeningTimes='05:00 - 00:00',
                    ),
                    ApcoaOpeningHoursInput(
                        Weekday=ApcoaOpeningHoursWeekday.THURSDAY,
                        OpeningTimes='05:00 - 02:00',
                    ),
                    ApcoaOpeningHoursInput(
                        Weekday=ApcoaOpeningHoursWeekday.FRIDAY,
                        OpeningTimes='05:00 - 02:00',
                    ),
                    ApcoaOpeningHoursInput(
                        Weekday=ApcoaOpeningHoursWeekday.SATURDAY,
                        OpeningTimes='05:00 - 02:00',
                    ),
                    ApcoaOpeningHoursInput(
                        Weekday=ApcoaOpeningHoursWeekday.SUNDAY,
                        OpeningTimes='05:00 - 02:00',
                    ),
                ],
                'Mo 05:00-24:00; Tu 05:00-24:00; We 05:00-24:00; Th 05:00-02:00; Fr 05:00-02:00; Sa 05:00-02:00; Su 05:00-02:00',
            ),
        ],
    )
    def test_get_osm_opening_hours(opening_times: list[ApcoaOpeningHoursInput], osm_opening_hours: str):
        apcoa_parking_site_input = ApcoaParkingSiteInput(
            CarParkId=1,
            CarparkLongName=None,
            CarparkShortName=None,
            CarParkWebsiteURL=None,
            CarParkPhotoURLs=None,
            CarparkType=ApcoaCarparkTypeNameInput(
                Name='example name',
            ),
            Address=ApcoaAdressInput(
                Street=None,
                Zip=None,
                City=None,
                Region=None,
            ),
            NavigationLocations=[],
            Spaces=[
                ApcoaParkingSpaceInput(
                    Type=ApcoaParkingSpaceType.TOTAL_SPACES,
                    Count=10,
                ),
            ],
            OpeningHours=opening_times,
            LastModifiedDateTime=datetime(2024, 4, 1, 10),
            IndicativeTariff=None,
        )
        assert apcoa_parking_site_input.get_osm_opening_hours() == osm_opening_hours
