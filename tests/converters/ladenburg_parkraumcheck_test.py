"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import json
from unittest.mock import Mock

import pytest

from parkapi_sources.converters import LadenburgParkraumcheckPushConverter
from parkapi_sources.util import RequestHelper
from tests.converters.helper import get_data_path, validate_static_parking_site_inputs


@pytest.fixture
def ladenburg_parkraumcheck_push_converter(
    mocked_config_helper: Mock, request_helper: RequestHelper
) -> LadenburgParkraumcheckPushConverter:
    return LadenburgParkraumcheckPushConverter(config_helper=mocked_config_helper, request_helper=request_helper)


class LadenburgParkraumcheckPushConverterTest:
    @staticmethod
    def test_get_static_parking_sites(ladenburg_parkraumcheck_push_converter: LadenburgParkraumcheckPushConverter):
        with get_data_path('ladenburg_parkraumcheck.geojson').open() as ladenburg_parkraumcheck_file:
            ladenburg_parkraumcheck_data = json.loads(ladenburg_parkraumcheck_file.read())

        static_parking_site_inputs, import_parking_site_exceptions = ladenburg_parkraumcheck_push_converter.handle_json(
            ladenburg_parkraumcheck_data,
        )

        assert len(static_parking_site_inputs) == 463
        assert len(import_parking_site_exceptions) == 0

        validate_static_parking_site_inputs(static_parking_site_inputs)
