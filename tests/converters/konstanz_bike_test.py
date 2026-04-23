"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from unittest.mock import Mock

import pytest

from parkapi_sources.converters import KonstanzBikePullConverter
from parkapi_sources.util import RequestHelper
from tests.converters.helper import validate_static_parking_site_inputs


@pytest.fixture
def konstanz_bike_pull_converter(
    mocked_config_helper: Mock, request_helper: RequestHelper
) -> KonstanzBikePullConverter:
    return KonstanzBikePullConverter(config_helper=mocked_config_helper, request_helper=request_helper)


class KonstanzBikePushConverterTest:
    @staticmethod
    def test_get_static_parking_sites(konstanz_bike_pull_converter: KonstanzBikePullConverter):
        static_parking_site_inputs, import_parking_site_exceptions = (
            konstanz_bike_pull_converter.get_static_parking_sites()
        )
        assert len(static_parking_site_inputs) == 246
        assert len(import_parking_site_exceptions) == 95

        validate_static_parking_site_inputs(static_parking_site_inputs)
