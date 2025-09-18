"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from pathlib import Path
from unittest.mock import Mock

from requests_mock import Mocker

from parkapi_sources.converters import FreiburgDisabledSensorsPullConverter, FreiburgPullConverter
from parkapi_sources.models import ExternalIdentifierInput
from parkapi_sources.util import RequestHelper
from tests.converters.helper import validate_static_parking_site_inputs, validate_static_parking_spot_inputs


def test_get_static_parking_sites_patched(
    mocked_config_helper: Mock,
    request_helper: RequestHelper,
    requests_mock: Mocker,
):
    config = {
        'PARK_API_PARKING_SITE_PATCH_DIR': Path(Path(__file__).parent, 'data', 'patches', 'parking_sites'),
        'STATIC_GEOJSON_BASE_URL': 'https://raw.githubusercontent.com/ParkenDD/parkapi-static-data/main/sources',
    }
    mocked_config_helper.get.side_effect = lambda key, default=None: config.get(key, default)
    patch_static_parking_site_pull_converter = FreiburgPullConverter(
        config_helper=mocked_config_helper,
        request_helper=request_helper,
    )

    # We need to get GeoJSON data
    requests_mock.real_http = True

    json_path = Path(Path(__file__).parent, 'data', 'freiburg.json')
    with json_path.open() as json_file:
        json_data = json_file.read()

    requests_mock.get('https://geoportal.freiburg.de/wfs/gdm_pls/gdm_plslive', text=json_data)

    static_parking_site_inputs, import_parking_site_exceptions = (
        patch_static_parking_site_pull_converter.get_static_parking_sites()
    )

    assert len(static_parking_site_inputs) == 20
    assert len(import_parking_site_exceptions) == 1

    assert static_parking_site_inputs[0].name == 'New name'
    assert isinstance(static_parking_site_inputs[0].external_identifiers[0], ExternalIdentifierInput)

    validate_static_parking_site_inputs(static_parking_site_inputs)


def test_get_static_parking_spots(
    request_helper: RequestHelper,
    mocked_config_helper: Mock,
    requests_mock: Mocker,
):
    config = {'PARK_API_PARKING_SPOT_PATCH_DIR': Path(Path(__file__).parent, 'data', 'patches', 'parking_spots')}
    mocked_config_helper.get.side_effect = lambda key, default=None: config.get(key, default)
    freiburg_disabled_sensors_pull_converter = FreiburgDisabledSensorsPullConverter(
        config_helper=mocked_config_helper,
        request_helper=request_helper,
    )

    json_path = Path(Path(__file__).parent, 'data', 'freiburg_disabled_sensors.geojson')
    with json_path.open() as json_file:
        json_data = json_file.read()

    requests_mock.get(
        'https://geoportal.freiburg.de/wfs/gdm_parkpl/gdm_parkpl?SERVICE=WFS&REQUEST=GetFeature&SRSNAME=EPSG:4326'
        '&SERVICE=WFS&VERSION=2.0.0&TYPENAMES=beh_parkpl_ueberw&OUTPUTFORMAT=geojson',
        text=json_data,
    )

    static_parking_spot_inputs, import_parking_spot_exceptions = (
        freiburg_disabled_sensors_pull_converter.get_static_parking_spots()
    )
    assert len(static_parking_spot_inputs) == 20
    assert len(import_parking_spot_exceptions) == 0

    assert static_parking_spot_inputs[0].name == 'New name'
    assert isinstance(static_parking_spot_inputs[0].external_identifiers[0], ExternalIdentifierInput)

    validate_static_parking_spot_inputs(static_parking_spot_inputs)
