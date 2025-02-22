"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from io import StringIO
from unittest.mock import Mock

import pytest

from parkapi_sources.converters import NeckarsulmBikePushConverter
from parkapi_sources.util import RequestHelper
from tests.converters.helper import get_data_path, validate_static_parking_site_inputs


@pytest.fixture
def neckarsulm_bike_push_converter(
    mocked_config_helper: Mock,
    request_helper: RequestHelper,
) -> NeckarsulmBikePushConverter:
    return NeckarsulmBikePushConverter(config_helper=mocked_config_helper, request_helper=request_helper)


class NeckarsulmPushConverterTest:
    @staticmethod
    def test_get_static_parking_sites(neckarsulm_bike_push_converter: NeckarsulmBikePushConverter):
        with get_data_path('neckarsulm_bike.csv').open() as neckarsulm_bike_file:
            neckarsulm_data = StringIO(neckarsulm_bike_file.read())

        static_parking_site_inputs, import_parking_site_exceptions = neckarsulm_bike_push_converter.handle_csv_string(
            neckarsulm_data,
        )

        assert len(static_parking_site_inputs) == 235
        assert len(import_parking_site_exceptions) == 1

        validate_static_parking_site_inputs(static_parking_site_inputs)
