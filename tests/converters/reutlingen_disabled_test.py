"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from io import StringIO
from unittest.mock import Mock

import pytest

from parkapi_sources.converters import ReutlingenDisabledPushConverter
from parkapi_sources.util import RequestHelper
from tests.converters.helper import get_data_path, validate_static_parking_spot_inputs


@pytest.fixture
def reutlingen_disabled_push_converter(
    mocked_config_helper: Mock, request_helper: RequestHelper
) -> ReutlingenDisabledPushConverter:
    return ReutlingenDisabledPushConverter(config_helper=mocked_config_helper, request_helper=request_helper)


class ReutlingenBikePushConverterTest:
    @staticmethod
    def test_get_static_parking_spots(reutlingen_disabled_push_converter: ReutlingenDisabledPushConverter):
        with get_data_path('reutlingen_disabled.csv').open() as reutlingen_disabled_file:
            reutlingen_disabled_data = StringIO(reutlingen_disabled_file.read())

        static_parking_spot_inputs, import_parking_spot_exceptions = (
            reutlingen_disabled_push_converter.handle_csv_string(
                reutlingen_disabled_data,
            )
        )

        assert len(static_parking_spot_inputs) == 44
        assert len(import_parking_spot_exceptions) == 0

        validate_static_parking_spot_inputs(static_parking_spot_inputs)
