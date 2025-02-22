"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from io import StringIO
from unittest.mock import Mock

import pytest

from parkapi_sources.converters import ReutlingenBikePushConverter
from parkapi_sources.util import RequestHelper
from tests.converters.helper import get_data_path, validate_static_parking_site_inputs


@pytest.fixture
def reutlingen_bike_push_converter(
    mocked_config_helper: Mock,
    request_helper: RequestHelper,
) -> ReutlingenBikePushConverter:
    return ReutlingenBikePushConverter(config_helper=mocked_config_helper, request_helper=request_helper)


class ReutlingenBikePushConverterTest:
    @staticmethod
    def test_get_static_parking_sites(reutlingen_bike_push_converter: ReutlingenBikePushConverter):
        with get_data_path('reutlingen_bike.csv').open() as reutlingen_bike_file:
            reutlingen_bike_data = StringIO(reutlingen_bike_file.read())

        static_parking_site_inputs, import_parking_site_exceptions = reutlingen_bike_push_converter.handle_csv_string(
            reutlingen_bike_data,
        )

        assert len(static_parking_site_inputs) == 332
        assert len(import_parking_site_exceptions) == 2

        validate_static_parking_site_inputs(static_parking_site_inputs)
