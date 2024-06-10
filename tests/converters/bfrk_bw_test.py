"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from io import StringIO
from unittest.mock import Mock

import pytest
from parkapi_sources.converters.bfrk_bw import BfrkBwSpnvBikePushConverter, BfrkBwSpnvCarPushConverter

from tests.converters.helper import get_data_path, validate_static_parking_site_inputs


@pytest.fixture
def bfrk_car_push_converter(mocked_config_helper: Mock) -> BfrkBwSpnvCarPushConverter:
    return BfrkBwSpnvCarPushConverter(config_helper=mocked_config_helper)


class BfrkCarPullConverterTest:
    @staticmethod
    def test_get_static_parking_sites(bfrk_car_push_converter: BfrkBwSpnvCarPushConverter):
        with get_data_path('bfrk_bw_car.csv').open() as bfrk_car_file:
            bfrk_car_data = StringIO(bfrk_car_file.read())

        static_parking_site_inputs, import_parking_site_exceptions = bfrk_car_push_converter.handle_csv_string(bfrk_car_data)

        assert len(static_parking_site_inputs) == 1555
        assert len(import_parking_site_exceptions) == 0

        validate_static_parking_site_inputs(static_parking_site_inputs)


@pytest.fixture
def bfrk_bike_push_converter(mocked_config_helper: Mock) -> BfrkBwSpnvBikePushConverter:
    return BfrkBwSpnvBikePushConverter(config_helper=mocked_config_helper)


class BfrkBikePullConverterTest:
    @staticmethod
    def test_get_static_parking_sites(bfrk_bike_push_converter: BfrkBwSpnvBikePushConverter):
        with get_data_path('bfrk_bw_bike.csv').open() as bfrk_bike_file:
            bfrk_bike_data = StringIO(bfrk_bike_file.read())

        static_parking_site_inputs, import_parking_site_exceptions = bfrk_bike_push_converter.handle_csv_string(bfrk_bike_data)

        assert len(static_parking_site_inputs) == 2000
        assert len(import_parking_site_exceptions) == 1  # One failure due invalid coordinate

        validate_static_parking_site_inputs(static_parking_site_inputs)
