"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import time
from pathlib import Path
from unittest.mock import Mock

import pytest
from requests_mock import Mocker

from parkapi_sources.converters import OpenDataSwissPullConverter
from parkapi_sources.converters.opendata_swiss.models import (
    OpenDataSwissAdditionalInformationInput,
    OpenDataSwissAddressInput,
    OpenDataSwissCapacitiesInput,
    OpenDataSwissCapacityCategoryType,
    OpenDataSwissOperationTimeDaysOfWeek,
    OpenDataSwissOperationTimeInput,
    OpenDataSwissParkingFacilityCategory,
    OpenDataSwissPropertiesInput,
)
from parkapi_sources.util import RequestHelper
from tests.converters.helper import validate_static_parking_site_inputs


@pytest.fixture
def requests_mock_opendata_swiss(requests_mock: Mocker) -> Mocker:
    json_path = Path(Path(__file__).parent, 'data', 'opendata_swiss.json')
    with json_path.open() as json_file:
        json_data = json_file.read()

    requests_mock.get(
        'https://data.opentransportdata.swiss/de/dataset/parking-facilities/permalink',
        text=json_data,
    )

    return requests_mock


@pytest.fixture
def opendata_swiss_pull_converter(
    mocked_config_helper: Mock, request_helper: RequestHelper
) -> OpenDataSwissPullConverter:
    return OpenDataSwissPullConverter(config_helper=mocked_config_helper, request_helper=request_helper)


class OpenDataSwissPullConverterTest:
    @staticmethod
    def test_get_static_parking_sites(
        opendata_swiss_pull_converter: OpenDataSwissPullConverter,
        requests_mock_opendata_swiss: Mocker,
    ):
        static_parking_site_inputs, import_parking_site_exceptions = (
            opendata_swiss_pull_converter.get_static_parking_sites()
        )

        assert len(static_parking_site_inputs) == 560
        assert len(import_parking_site_exceptions) == 0

        validate_static_parking_site_inputs(static_parking_site_inputs)


class OpenDataSwissParkingSiteInputTest:
    @staticmethod
    @pytest.mark.parametrize(
        'opening_times, osm_opening_hours',
        [
            # Test for 24/7
            (
                OpenDataSwissOperationTimeInput(
                    operatingFrom=time(0),
                    operatingTo=time(0),
                    daysOfWeek=[
                        OpenDataSwissOperationTimeDaysOfWeek.MONDAY,
                        OpenDataSwissOperationTimeDaysOfWeek.TUESDAY,
                        OpenDataSwissOperationTimeDaysOfWeek.WEDNESDAY,
                        OpenDataSwissOperationTimeDaysOfWeek.THURSDAY,
                        OpenDataSwissOperationTimeDaysOfWeek.FRIDAY,
                        OpenDataSwissOperationTimeDaysOfWeek.SATURDAY,
                        OpenDataSwissOperationTimeDaysOfWeek.SUNDAY,
                    ],
                ),
                '24/7',
            ),
            # Test for Sunday missing
            (
                OpenDataSwissOperationTimeInput(
                    operatingFrom=time(0),
                    operatingTo=time(0),
                    daysOfWeek=[
                        OpenDataSwissOperationTimeDaysOfWeek.MONDAY,
                        OpenDataSwissOperationTimeDaysOfWeek.TUESDAY,
                        OpenDataSwissOperationTimeDaysOfWeek.WEDNESDAY,
                        OpenDataSwissOperationTimeDaysOfWeek.THURSDAY,
                        OpenDataSwissOperationTimeDaysOfWeek.FRIDAY,
                        OpenDataSwissOperationTimeDaysOfWeek.SATURDAY,
                    ],
                ),
                'Mo-Fr 00:00-24:00; Sa 00:00-24:00',
            ),
            # Test for Wednesday missing
            (
                OpenDataSwissOperationTimeInput(
                    operatingFrom=time(0),
                    operatingTo=time(0),
                    daysOfWeek=[
                        OpenDataSwissOperationTimeDaysOfWeek.MONDAY,
                        OpenDataSwissOperationTimeDaysOfWeek.TUESDAY,
                        OpenDataSwissOperationTimeDaysOfWeek.THURSDAY,
                        OpenDataSwissOperationTimeDaysOfWeek.FRIDAY,
                        OpenDataSwissOperationTimeDaysOfWeek.SATURDAY,
                        OpenDataSwissOperationTimeDaysOfWeek.SUNDAY,
                    ],
                ),
                'Mo 00:00-24:00; Tu 00:00-24:00; Th 00:00-24:00; Fr 00:00-24:00; Sa 00:00-24:00; Su 00:00-24:00',
                # Even better, but more complicated: 'Mo-Tu 00:00-24:00; Th-Fr 00:00-24:00; Sa-So 00:00-24:00'
            ),
            # Test for all day open at weekday, but not open at weekend
            (
                OpenDataSwissOperationTimeInput(
                    operatingFrom=time(0),
                    operatingTo=time(0),
                    daysOfWeek=[
                        OpenDataSwissOperationTimeDaysOfWeek.MONDAY,
                        OpenDataSwissOperationTimeDaysOfWeek.TUESDAY,
                        OpenDataSwissOperationTimeDaysOfWeek.WEDNESDAY,
                        OpenDataSwissOperationTimeDaysOfWeek.THURSDAY,
                        OpenDataSwissOperationTimeDaysOfWeek.FRIDAY,
                    ],
                ),
                'Mo-Fr 00:00-24:00',
            ),
            # Test for all day open at weekend, but not open at weekday
            (
                OpenDataSwissOperationTimeInput(
                    operatingFrom=time(0),
                    operatingTo=time(0),
                    daysOfWeek=[
                        OpenDataSwissOperationTimeDaysOfWeek.SATURDAY,
                        OpenDataSwissOperationTimeDaysOfWeek.SUNDAY,
                    ],
                ),
                'Sa 00:00-24:00; Su 00:00-24:00',
            ),
        ],
    )
    def test_get_osm_opening_hours(opening_times: dict[OpenDataSwissOperationTimeInput], osm_opening_hours: str):
        opendata_swiss_parking_site_input = OpenDataSwissPropertiesInput(
            operator=None,
            displayName=None,
            address=OpenDataSwissAddressInput(
                addressLine=None,
                city=None,
                postalCode=None,
            ),
            capacities=[
                OpenDataSwissCapacitiesInput(
                    categoryType=OpenDataSwissCapacityCategoryType.STANDARD,
                    total=10,
                )
            ],
            additionalInformationForCustomers=OpenDataSwissAdditionalInformationInput(
                de=None,
                en=None,
                it=None,
                fr=None,
            ),
            parkingFacilityCategory=OpenDataSwissParkingFacilityCategory.CAR,
            parkingFacilityType=None,
            salesChannels=[],
            operationTime=opening_times,
        )

        assert opendata_swiss_parking_site_input.get_osm_opening_hours() == osm_opening_hours
