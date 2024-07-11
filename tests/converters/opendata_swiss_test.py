"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from pathlib import Path
from unittest.mock import Mock

import pytest
from parkapi_sources.converters import OpenDataSwissPullConverter
from parkapi_sources.converters.opendata_swiss.models import (
    OpenDataSwissAdditionalInformationInput,
    OpenDataSwissAddressInput,
    OpenDataSwissCapacitiesInput,
    OpenDataSwissCapacityCategoryTypeInput,
    OpenDataSwissOperationTimeDaysOfWeek,
    OpenDataSwissOperationTimeInput,
    OpenDataSwissPropertiesInput,
)
from requests_mock import Mocker

from tests.converters.helper import validate_static_parking_site_inputs


@pytest.fixture
def requests_mock_opendata_swiss(requests_mock: Mocker) -> Mocker:
    json_path = Path(Path(__file__).parent, 'data', 'opendata_swiss.json')
    with json_path.open() as json_file:
        json_data = json_file.read()

    requests_mock.get(
        'https://opentransportdata.swiss/dataset/c1be030e-adad-41c6-8ee2-899e85f840f6/resource/5dab3aba-6b5a-42cb-bb73-103fb28c7e10/download/parking-facilities.json',
        text=json_data,
    )

    return requests_mock


@pytest.fixture
def opendata_swiss_pull_converter(mocked_config_helper: Mock) -> OpenDataSwissPullConverter:
    return OpenDataSwissPullConverter(config_helper=mocked_config_helper)


class OpenDataSwissPullConverterTest:
    @staticmethod
    def test_get_static_parking_sites(opendata_swiss_pull_converter: OpenDataSwissPullConverter, requests_mock_opendata_swiss: Mocker):
        static_parking_site_inputs, import_parking_site_exceptions = opendata_swiss_pull_converter.get_static_parking_sites()

        assert len(static_parking_site_inputs) > len(
            import_parking_site_exceptions
        ), 'There should be more valid then invalid parking sites'

        validate_static_parking_site_inputs(static_parking_site_inputs)


class OpenDataSwissParkingSiteInputTest:
    @staticmethod
    @pytest.mark.parametrize(
        'opening_times, osm_opening_hours',
        [
            # Test for 24/7
            (
                OpenDataSwissOperationTimeInput(
                    operatingFrom='00:00:00',
                    operatingTo='00:00:00',
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
                    operatingFrom='00:00:00',
                    operatingTo='00:00:00',
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
                    operatingFrom='00:00:00',
                    operatingTo='00:00:00',
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
                    operatingFrom='00:00:00',
                    operatingTo='00:00:00',
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
                    operatingFrom='00:00:00',
                    operatingTo='00:00:00',
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
                    categoryType=OpenDataSwissCapacityCategoryTypeInput.STANDARD,
                    total=10,
                )
            ],
            additionalInformationForCustomers=OpenDataSwissAdditionalInformationInput(
                de=None,
                en=None,
                it=None,
                fr=None,
            ),
            parkingFacilityCategory=None,
            parkingFacilityType=None,
            salesChannels=[],
            operationTime=opening_times,
        )

        assert opendata_swiss_parking_site_input.get_osm_opening_hours() == osm_opening_hours
