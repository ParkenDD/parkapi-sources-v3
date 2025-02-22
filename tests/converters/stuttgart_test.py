"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from unittest.mock import Mock

import pytest
from lxml import etree

from parkapi_sources.converters import StuttgartPushConverter
from parkapi_sources.util import RequestHelper
from tests.converters.helper import (
    get_data_path,
    validate_realtime_parking_site_inputs,
    validate_static_parking_site_inputs,
)


@pytest.fixture
def stuttgart_push_converter(mocked_config_helper: Mock, request_helper: RequestHelper) -> StuttgartPushConverter:
    return StuttgartPushConverter(config_helper=mocked_config_helper, request_helper=request_helper)


class StuttgartPullConverterTest:
    @staticmethod
    def test_get_static_parking_sites(stuttgart_push_converter: StuttgartPushConverter):
        with get_data_path('stuttgart-static.xml').open('br') as xml_file:
            root_element = etree.fromstring(xml_file.read(), parser=etree.XMLParser(resolve_entities=False))  # noqa: S320

        static_parking_site_inputs, import_parking_site_exceptions = stuttgart_push_converter.handle_xml(root_element)

        assert len(static_parking_site_inputs) == 48
        assert len(import_parking_site_exceptions) == 1

        validate_static_parking_site_inputs(static_parking_site_inputs)

    @staticmethod
    def test_get_realtime_parking_sites(stuttgart_push_converter: StuttgartPushConverter):
        with get_data_path('stuttgart-realtime.xml').open('br') as xml_file:
            root_element = etree.fromstring(xml_file.read(), parser=etree.XMLParser(resolve_entities=False))  # noqa: S320

        realtime_parking_site_inputs, import_parking_site_exceptions = stuttgart_push_converter.handle_xml(root_element)

        assert len(realtime_parking_site_inputs) == 49
        assert len(import_parking_site_exceptions) == 0

        validate_realtime_parking_site_inputs(realtime_parking_site_inputs)
