"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from unittest.mock import Mock

import pytest

from parkapi_sources.converters.herrenberg import HerrenbergPullConverter
from tests.converters.helper import validate_static_parking_site_inputs


@pytest.fixture
def herrenberg_config_helper(mocked_config_helper: Mock):
    config = {
    }
    mocked_config_helper.get.side_effect = lambda key, default=None: config.get(key, default)
    return mocked_config_helper


@pytest.fixture
def herrenberg_pull_converter(herrenberg_config_helper: Mock, ) -> HerrenbergPullConverter:
    return HerrenbergPullConverter(config_helper=herrenberg_config_helper)


class HerrenbergPullConverterTest:
    @staticmethod
    def test_get_static_parking_sites(herrenberg_pull_converter: HerrenbergPullConverter):
        static_parking_site_inputs, import_parking_site_exceptions = herrenberg_pull_converter.get_static_parking_sites()
        assert len(static_parking_site_inputs) < len(
            import_parking_site_exceptions
        ), 'There should be more valid then invalid parking sites'

        validate_static_parking_site_inputs(static_parking_site_inputs)

    @staticmethod
    def test_get_realtime_parking_sites(herrenberg_pull_converter: HerrenbergPullConverter):
        herrenberg_pull_converter.get_realtime_parking_sites(herrenberg_pull_converter)

