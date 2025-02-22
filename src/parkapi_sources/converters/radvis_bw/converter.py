"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import pyproj
from validataclass.exceptions import ValidationError
from validataclass.validators import DataclassValidator

from parkapi_sources.converters.base_converter.pull import PullConverter
from parkapi_sources.exceptions import ImportParkingSiteException
from parkapi_sources.models import GeojsonInput, RealtimeParkingSiteInput, SourceInfo, StaticParkingSiteInput

from .models import RadvisFeatureInput


class RadvisBwPullConverter(PullConverter):
    proj: pyproj.Proj = pyproj.Proj(proj='utm', zone=32, ellps='WGS84', preserve_units=True)
    _base_url = (
        'https://radvis.landbw.de/api/geoserver/basicauth/radvis/wfs?service=WFS&version=2.0.0&request='
        'GetFeature&typeNames=radvis%3Aabstellanlage&outputFormat=application/json'
    )
    required_config_keys = ['PARK_API_RADVIS_USER', 'PARK_API_RADVIS_PASSWORD']

    geojson_validator = DataclassValidator(GeojsonInput)
    radvis_parking_site_validator = DataclassValidator(RadvisFeatureInput)

    source_info = SourceInfo(
        uid='radvis_bw',
        name='RadVIS BW',
        public_url='https://www.aktivmobil-bw.de/radverkehr/raddaten/radvis-bw/',
        has_realtime_data=False,
    )

    def get_static_parking_sites(self) -> tuple[list[StaticParkingSiteInput], list[ImportParkingSiteException]]:
        static_parking_site_inputs: list[StaticParkingSiteInput] = []
        static_parking_site_errors: list[ImportParkingSiteException] = []

        parking_site_features = self.geojson_validator.validate(self.get_data())
        sources_to_ignore: list[str] = []
        if self.config_helper.get('PARK_API_RADVIS_IGNORE_SOURCES'):
            sources_to_ignore = self.config_helper.get('PARK_API_RADVIS_IGNORE_SOURCES')

        for feature_dict in parking_site_features.features:
            try:
                radvis_parking_site_input = self.radvis_parking_site_validator.validate(feature_dict)

                # Ignore sources by config, because Radvis has a lot of duplicate data if you import data from other sources, too.
                if radvis_parking_site_input.properties.quell_system in sources_to_ignore:
                    continue

                static_parking_site_inputs += radvis_parking_site_input.to_static_parking_site_inputs_with_proj(
                    self.proj,
                )

            except ValidationError as e:
                static_parking_site_errors.append(
                    ImportParkingSiteException(
                        source_uid=self.source_info.uid,
                        parking_site_uid=feature_dict.get('properties', {}).get('id'),
                        message=f'validation error for data {feature_dict}: {e.to_dict()}',
                    ),
                )

        return static_parking_site_inputs, static_parking_site_errors

    def get_realtime_parking_sites(self) -> tuple[list[RealtimeParkingSiteInput], list[ImportParkingSiteException]]:
        return [], []

    def get_data(self) -> dict:
        response = self.request_get(
            url=self._base_url,
            auth=(self.config_helper.get('PARK_API_RADVIS_USER'), self.config_helper.get('PARK_API_RADVIS_PASSWORD')),
            timeout=30,
        )

        return response.json()
