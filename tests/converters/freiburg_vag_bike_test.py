from pathlib import Path
from unittest.mock import Mock

import pytest
from requests_mock import Mocker

from parkapi_sources.converters.freiburg_vag_bike import FreiburgVAGBikePullConverter
from parkapi_sources.util import RequestHelper
from tests.converters.helper import validate_static_parking_site_inputs


@pytest.fixture
def freiburg_vag_bike_pull_converter(
    mocked_config_helper: Mock,
    request_helper: RequestHelper,
) -> FreiburgVAGBikePullConverter:
    return FreiburgVAGBikePullConverter(
        config_helper=mocked_config_helper,
        request_helper=request_helper,
    )


def requests_mock_freiburg_vag_bike(requests_mock: Mocker) -> Mocker:
    json_path = Path(Path(__file__).parent, 'data', 'freiburg_vag_bike.geojson')
    json_data = json_path.read_text()
    requests_mock.get(
        'https://geoportal.freiburg.de/wfs/vag_infra/vag_infra?SERVICE=WFS&version=2.0.0&REQUEST=GetFeature'
        '&typename=fahrradboxen&outputFormat=geojson&srsname=epsg:4326',
        text=json_data,
    )
    return requests_mock


class FreiburgVAGBikePullConverterTest:
    @staticmethod
    def test_get_static_parking_sites(
        freiburg_vag_bike_pull_converter: FreiburgVAGBikePullConverter,
        requests_mock: Mocker,
    ):
        json_path = Path(Path(__file__).parent, 'data', 'freiburg_vag_bike.geojson')
        json_data = json_path.read_text()
        requests_mock.get(
            'https://geoportal.freiburg.de/wfs/vag_infra/vag_infra?SERVICE=WFS&version=2.0.0&REQUEST=GetFeature'
            '&typename=fahrradboxen&outputFormat=geojson&srsname=epsg:4326',
            text=json_data,
        )

        static_parking_site_inputs, import_parking_site_exceptions = (
            freiburg_vag_bike_pull_converter.get_static_parking_sites()
        )

        assert len(static_parking_site_inputs) == 8
        assert len(import_parking_site_exceptions) == 0

        validate_static_parking_site_inputs(static_parking_site_inputs)
