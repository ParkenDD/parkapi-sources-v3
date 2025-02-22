"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from pathlib import Path
from unittest.mock import Mock

import pytest
from requests_mock import Mocker

from parkapi_sources.converters.bfrk_bw import BfrkBwBikePushConverter, BfrkBwCarPushConverter
from parkapi_sources.util import RequestHelper
from tests.converters.helper import validate_static_parking_site_inputs


@pytest.fixture
def mocked_bfrk_bw_config_helper(mocked_config_helper: Mock):
    config = {}
    mocked_config_helper.get.side_effect = lambda key, default=None: config.get(key, default)
    return mocked_config_helper


@pytest.fixture
def bfrk_car_push_converter(
    mocked_bfrk_bw_config_helper: Mock, request_helper: RequestHelper
) -> BfrkBwCarPushConverter:
    return BfrkBwCarPushConverter(config_helper=mocked_bfrk_bw_config_helper, request_helper=request_helper)


class BfrkCarPullConverterTest:
    @staticmethod
    def test_get_static_parking_sites(bfrk_car_push_converter: BfrkBwCarPushConverter, requests_mock: Mocker):
        json_path = Path(Path(__file__).parent, 'data', 'bfrk_bw_car.json')
        with json_path.open() as json_file:
            json_data = json_file.read()

        requests_mock.get(
            'https://bfrk-kat-api.efa-bw.de/bfrk_api/parkplaetze',
            text=json_data,
        )

        static_parking_site_inputs, import_parking_site_exceptions = bfrk_car_push_converter.get_static_parking_sites()

        assert len(static_parking_site_inputs) == 2233
        assert len(import_parking_site_exceptions) == 30

        validate_static_parking_site_inputs(static_parking_site_inputs)


@pytest.fixture
def bfrk_bike_push_converter(
    mocked_bfrk_bw_config_helper: Mock, request_helper: RequestHelper
) -> BfrkBwBikePushConverter:
    return BfrkBwBikePushConverter(config_helper=mocked_bfrk_bw_config_helper, request_helper=request_helper)


class BfrkBikePullConverterTest:
    @staticmethod
    def test_get_static_parking_sites(bfrk_bike_push_converter: BfrkBwBikePushConverter, requests_mock: Mocker):
        json_path = Path(Path(__file__).parent, 'data', 'bfrk_bw_bike.json')
        with json_path.open() as json_file:
            json_data = json_file.read()

        requests_mock.get(
            'https://bfrk-kat-api.efa-bw.de/bfrk_api/fahrradanlagen',
            text=json_data,
        )

        static_parking_site_inputs, import_parking_site_exceptions = bfrk_bike_push_converter.get_static_parking_sites()

        assert len(static_parking_site_inputs) == 2780
        assert len(import_parking_site_exceptions) == 74

        validate_static_parking_site_inputs(static_parking_site_inputs)
