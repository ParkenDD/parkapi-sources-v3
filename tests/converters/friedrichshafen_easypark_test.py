"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from io import StringIO
from unittest.mock import Mock

import pytest

from parkapi_sources.converters.friedrichshafen_easypark.converter import FriedrichshafenEasyParkPushConverter
from parkapi_sources.util import RequestHelper
from tests.converters.helper import get_data_path, validate_static_parking_site_inputs


@pytest.fixture
def friedrichshafen_easypark_push_converter(
    mocked_config_helper: Mock, request_helper: RequestHelper
) -> FriedrichshafenEasyParkPushConverter:
    return FriedrichshafenEasyParkPushConverter(config_helper=mocked_config_helper, request_helper=request_helper)


class FriedrichshafenEasyParkPushConverterTest:
    @staticmethod
    def test_get_static_parking_sites(friedrichshafen_easypark_push_converter: FriedrichshafenEasyParkPushConverter):
        with get_data_path('friedrichshafen_inventory.csv').open(encoding='utf-8-sig') as friedrichshafen_easypark_file:
            friedrichshafen_easypark_data = StringIO(friedrichshafen_easypark_file.read())

        static_parking_site_inputs, import_parking_site_exceptions = (
            friedrichshafen_easypark_push_converter.handle_csv_string(friedrichshafen_easypark_data)
        )

        assert len(static_parking_site_inputs) == 1681
        assert len(import_parking_site_exceptions) == 16

        validate_static_parking_site_inputs(static_parking_site_inputs)
