"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from unittest.mock import Mock

import pytest
from openpyxl.reader.excel import load_workbook

from parkapi_sources.converters import HuefnerPushConverter
from parkapi_sources.util import RequestHelper
from tests.converters.helper import get_data_path, validate_static_parking_site_inputs


@pytest.fixture
def huefner_push_converter(mocked_config_helper: Mock, request_helper: RequestHelper) -> HuefnerPushConverter:
    return HuefnerPushConverter(config_helper=mocked_config_helper, request_helper=request_helper)


class HuefnerPushConverterTest:
    @staticmethod
    def test_get_static_parking_sites(huefner_push_converter: HuefnerPushConverter):
        workbook = load_workbook(filename=str(get_data_path('huefner.xlsx').absolute()))

        static_parking_site_inputs, import_parking_site_exceptions = huefner_push_converter.handle_xlsx(workbook)

        assert len(static_parking_site_inputs) == 21
        assert len(import_parking_site_exceptions) == 18

        validate_static_parking_site_inputs(static_parking_site_inputs)
