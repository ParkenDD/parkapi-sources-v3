"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from io import StringIO
from unittest.mock import Mock

import pytest

from parkapi_sources.converters import KonstanzBikePushConverter
from parkapi_sources.util import RequestHelper
from tests.converters.helper import get_data_path, validate_static_parking_site_inputs


@pytest.fixture
def konstanz_bike_push_converter(
    mocked_config_helper: Mock, request_helper: RequestHelper
) -> KonstanzBikePushConverter:
    return KonstanzBikePushConverter(config_helper=mocked_config_helper, request_helper=request_helper)


class KonstanzBikePushConverterTest:
    @staticmethod
    def test_get_static_parking_sites(konstanz_bike_push_converter: KonstanzBikePushConverter):
        with get_data_path('konstanz_bike.csv').open() as konstanz_bike_file:
            konstanz_bike_data = StringIO(konstanz_bike_file.read())

        static_parking_site_inputs, import_parking_site_exceptions = konstanz_bike_push_converter.handle_csv_string(
            konstanz_bike_data,
        )

        assert len(static_parking_site_inputs) == 162
        assert len(import_parking_site_exceptions) == 5

        validate_static_parking_site_inputs(static_parking_site_inputs)
