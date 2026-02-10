"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from pathlib import Path
from unittest.mock import Mock

import pytest
from requests_mock import Mocker

from parkapi_sources.converters.bielefeld import BielefeldPullConverter
from parkapi_sources.util import RequestHelper
from tests.converters.helper import validate_static_parking_site_inputs


@pytest.fixture
def bielefeld_pull_converter(mocked_config_helper: Mock, request_helper: RequestHelper) -> BielefeldPullConverter:
    return BielefeldPullConverter(config_helper=mocked_config_helper, request_helper=request_helper)


class BielefeldPullConverterTest:
    @staticmethod
    def test_get_static_parking_sites(bielefeld_pull_converter: BielefeldPullConverter, requests_mock: Mocker):
        csv_path = Path(Path(__file__).parent, 'data', 'bielefeld.csv')
        with csv_path.open() as csv_file:
            csv_data = csv_file.read()

        requests_mock.get(
            'https://www.bielefeld01.de/md/WFS/parkplaetze/01?SERVICE=WFS&VERSION=1.1.0&REQUEST=GetFeature'
            '&TYPENAME=parkplaetze_p&SRSNAME=EPSG:4326&OUTPUTFORMAT=text/csv'
            '&NW_INFO=/parkplaetze_p_EPSG25832_CSV.csv',
            text=csv_data,
        )

        static_parking_site_inputs, import_parking_site_exceptions = bielefeld_pull_converter.get_static_parking_sites()

        assert len(static_parking_site_inputs) == 853
        assert len(import_parking_site_exceptions) == 0

        validate_static_parking_site_inputs(static_parking_site_inputs)
