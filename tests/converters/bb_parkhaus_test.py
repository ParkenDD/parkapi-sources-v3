"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from unittest.mock import Mock

import pytest
from openpyxl.reader.excel import load_workbook

from parkapi_sources.converters import BBParkhausPushConverter
from parkapi_sources.util import RequestHelper
from tests.converters.helper import get_data_path, validate_static_parking_site_inputs


@pytest.fixture
def bb_parkhaus_push_converter(mocked_config_helper: Mock, request_helper: RequestHelper) -> BBParkhausPushConverter:
    return BBParkhausPushConverter(config_helper=mocked_config_helper, request_helper=request_helper)


class BBParkhausPushConverterTest:
    @staticmethod
    def test_get_static_parking_sites(bb_parkhaus_push_converter: BBParkhausPushConverter):
        workbook = load_workbook(filename=str(get_data_path('bb_parkhaus.xlsx').absolute()))

        static_parking_site_inputs, import_parking_site_exceptions = bb_parkhaus_push_converter.handle_xlsx(workbook)

        assert len(static_parking_site_inputs) == 26
        assert len(import_parking_site_exceptions) == 0

        validate_static_parking_site_inputs(static_parking_site_inputs)
