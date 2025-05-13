"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from pathlib import Path
from unittest.mock import Mock

import pytest
from _pytest.fixtures import FixtureRequest
from requests_mock import Mocker

from parkapi_sources.converters import (
    VrsBondorfPullConverter,
    VrsKirchheimPullConverter,
    VrsNeustadtPullConverter,
    VrsVaihingenPullConverter,
)
from parkapi_sources.util import RequestHelper
from tests.converters.helper import validate_realtime_parking_site_inputs, validate_static_parking_site_inputs


@pytest.fixture
def vrs_config_helper(mocked_config_helper: Mock):
    config = {
        'PARK_API_MOBILITHEK_CERT': '/dev/null',
        'PARK_API_MOBILITHEK_KEY': '/dev/null',
        'PARK_API_MOBILITHEK_VRS_BONDORF_STATIC_SUBSCRIPTION_ID': 1234567890,
        'PARK_API_MOBILITHEK_VRS_BONDORF_REALTIME_SUBSCRIPTION_ID': 1234567890,
        'PARK_API_MOBILITHEK_VRS_KIRCHHEIM_STATIC_SUBSCRIPTION_ID': 1234567890,
        'PARK_API_MOBILITHEK_VRS_KIRCHHEIM_REALTIME_SUBSCRIPTION_ID': 1234567890,
        'PARK_API_MOBILITHEK_VRS_NEUSTADT_STATIC_SUBSCRIPTION_ID': 1234567890,
        'PARK_API_MOBILITHEK_VRS_NEUSTADT_REALTIME_SUBSCRIPTION_ID': 1234567890,
        'PARK_API_MOBILITHEK_VRS_VAIHINGEN_STATIC_SUBSCRIPTION_ID': 1234567890,
        'PARK_API_MOBILITHEK_VRS_VAIHINGEN_REALTIME_SUBSCRIPTION_ID': 1234567890,
    }
    mocked_config_helper.get.side_effect = lambda key, default=None: config.get(key, default)
    return mocked_config_helper


@pytest.fixture
def vrs_bondorf_pull_converter(
    vrs_config_helper: Mock,
    request_helper: RequestHelper,
) -> VrsBondorfPullConverter:
    return VrsBondorfPullConverter(config_helper=vrs_config_helper, request_helper=request_helper)


@pytest.fixture
def vrs_kirchheim_pull_converter(
    vrs_config_helper: Mock,
    request_helper: RequestHelper,
) -> VrsKirchheimPullConverter:
    return VrsKirchheimPullConverter(config_helper=vrs_config_helper, request_helper=request_helper)


@pytest.fixture
def vrs_neustadt_pull_converter(
    vrs_config_helper: Mock,
    request_helper: RequestHelper,
) -> VrsNeustadtPullConverter:
    return VrsNeustadtPullConverter(config_helper=vrs_config_helper, request_helper=request_helper)


@pytest.fixture
def vrs_vaihingen_pull_converter(
    vrs_config_helper: Mock,
    request_helper: RequestHelper,
) -> VrsVaihingenPullConverter:
    return VrsVaihingenPullConverter(config_helper=vrs_config_helper, request_helper=request_helper)


class VrsVaihingenConverterTest:
    @pytest.mark.parametrize(
        'converter_name, filename, result_count',
        [
            ('vrs_bondorf_pull_converter', 'vrs_bondorf-static.xml', 1),
            ('vrs_kirchheim_pull_converter', 'vrs_kirchheim-static.xml', 2),
            ('vrs_neustadt_pull_converter', 'vrs_neustadt-static.xml', 2),
            ('vrs_vaihingen_pull_converter', 'vrs_vaihingen-static.xml', 1),
        ],
    )
    def test_get_static_parking_sites(
        self,
        requests_mock: Mocker,
        request: FixtureRequest,
        converter_name: str,
        filename: str,
        result_count: int,
    ):
        xml_path = Path(Path(__file__).parent, 'data', filename)
        with xml_path.open() as xml_file:
            xml_data = xml_file.read()

        requests_mock.get(
            'https://mobilithek.info:8443/mobilithek/api/v1.0/subscription/1234567890/clientPullService?subscriptionID=1234567890',
            text=xml_data,
        )
        converter = request.getfixturevalue(converter_name)

        static_parking_site_inputs, import_parking_site_exceptions = converter.get_static_parking_sites()

        assert len(static_parking_site_inputs) == result_count
        assert len(import_parking_site_exceptions) == 0

        validate_static_parking_site_inputs(static_parking_site_inputs)

    @pytest.mark.parametrize(
        'converter_name, filename, result_count',
        [
            ('vrs_bondorf_pull_converter', 'vrs_bondorf-realtime.xml', 1),
            ('vrs_kirchheim_pull_converter', 'vrs_kirchheim-realtime.xml', 2),
            ('vrs_neustadt_pull_converter', 'vrs_neustadt-realtime.xml', 2),
            ('vrs_vaihingen_pull_converter', 'vrs_vaihingen-realtime.xml', 1),
        ],
    )
    def test_get_realtime_parking_sites(
        self,
        requests_mock: Mocker,
        request: FixtureRequest,
        converter_name: str,
        filename: str,
        result_count: int,
    ):
        xml_path = Path(Path(__file__).parent, 'data', filename)
        with xml_path.open() as xml_file:
            xml_data = xml_file.read()

        requests_mock.get(
            'https://mobilithek.info:8443/mobilithek/api/v1.0/subscription/1234567890/clientPullService?subscriptionID=1234567890',
            text=xml_data,
        )

        converter = request.getfixturevalue(converter_name)

        static_parking_site_inputs, import_parking_site_exceptions = converter.get_realtime_parking_sites()

        assert len(static_parking_site_inputs) == result_count
        assert len(import_parking_site_exceptions) == 0

        validate_realtime_parking_site_inputs(static_parking_site_inputs)
